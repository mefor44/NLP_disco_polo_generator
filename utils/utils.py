import requests
import re
from bs4 import BeautifulSoup
import sys
import time

class Tee(object):
    def __init__(self, name, mode, encoding="utf-8"):
        self.file = open(name, mode, encoding=encoding)
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()
    def write(self, data):
        self.file.write(data)
        try:
            self.stdout.write(data)
        except UnicodeEncodeError as err:
            self.stdout.write(f"Writing log didn't succeed due to {err}.")

    def flush(self):
        self.file.flush()


def robust_request(url, sleep_time=0.5):
    """
    A wrapper to make robust https requests.
    """
    status_code = 500  # Want to get a status-code of 200
    while status_code != 200:
        time.sleep(sleep_time)  # Don't ping the server too often
        try:
            r = requests.get(url)
            status_code = r.status_code
            if status_code != 200:
                print(f"Server Error! Response Code {r.status_code}. Retrying...")
        except:
            print("An exception has occurred, probably a momentory loss of connection. Waiting one seconds...")
            time.sleep(2)
    return r


def scrape_text(url, sleep_time):
    r = robust_request(url, sleep_time)
    soup = BeautifulSoup(r.text, "html.parser")
    tab = soup.findAll("div", attrs={"class": "inner-text"})
    # it may happen that a song won't have any text
    # then we return empty string
    if len(tab) == 0:
        return ""
    else:
        return tab[0].text


def clean_record(txt):
    newlines = txt.replace('\\n', '\n')
    return bytes(re.sub('\n+', '\n', re.sub(r"(Ref.+|[0-9]+\.|\\r|\r|(^ ))", '', newlines)), 'utf-8').decode('utf-8', 'ignore')



def scrape_band(url, verbose=True, sleep_time=0.5):
    r = robust_request(url, sleep_time)
    soup = BeautifulSoup(r.text, "html.parser")

    pages = [i.contents[0] for i in soup.findAll("a", attrs={"class": "page-link"})]
    page_nums = []
    for i in pages:
        try:
            page_nums.append(int(i))
        except ValueError:
            continue

    # if there is less than 31 hits there are no pages
    try:
        max_page_num = max(page_nums)
        # try to get active page number
        active = soup.find("li", attrs={"class": "page-item active"})
        active_page_num = int(active.find("a").contents[0])
    except ValueError:
        max_page_num = 1
        active_page_num = 1

    res = []

    # collect data for each page with music hits
    while active_page_num <= max_page_num:

        # collect all metadata
        tables = soup.findAll("div", attrs={"class": "ranking-lista"})
        tables = tables[0].findAll("a", attrs={"class": "title"})
        metadata = [(elem.get("title"), elem.get("href")) for elem in tables]

        # collect song texts
        for i, (title, link_end) in enumerate(metadata):
            # time.sleep(sleep_time)
            if verbose:
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)
                print(f"Song {i + 1}/30, page {active_page_num}/{max_page_num}, title = {title} (time: {current_time}).")
            full_link = "https://www.tekstowo.pl" + link_end
            scraped_text = scrape_text(full_link, sleep_time)
            if scraped_text != "":
                res.append(scraped_text)

        # update page counter
        active_page_num += 1
        # if the page wasn't the last update url,soup variables
        if active_page_num <= max_page_num:
            new_url = url+f",alfabetycznie,strona,{active_page_num}.html"
            r = robust_request(new_url, sleep_time)
            soup = BeautifulSoup(r.text, "html.parser")

    return res

