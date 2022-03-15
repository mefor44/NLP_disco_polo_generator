import requests
import re
from bs4 import BeautifulSoup
import sys
import time

class Tee(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
    def flush(self):
        self.file.flush()


def scrape_text(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    tab = soup.findAll("div", attrs={"class":"inner-text"})
    return tab[0].text


def clean_record(txt):
    newlines = txt.replace('\\n', '\n')
    return bytes(re.sub('\n+', '\n', re.sub(r"(Ref.+|[0-9]+\.|\\r|\r|(^ ))", '', newlines)), 'utf-8').decode('utf-8', 'ignore')



def scrape_band(url, verbose=True, sleep_time=0.5):
    r = requests.get(url)
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
            time.sleep(sleep_time)
            if verbose:
                print(f"Song {i + 1}/30, page {active_page_num}/{max_page_num}, title = {title}.")
            full_link = "https://www.tekstowo.pl" + link_end
            res.append(scrape_text(full_link))

        # update page counter
        active_page_num += 1
        # if the page wasn't the last update url,soup variables
        if active_page_num <= max_page_num:
            new_url = url+f",alfabetycznie,strona,{active_page_num}.html"
            r = requests.get(new_url)
            soup = BeautifulSoup(r.text, "html.parser")

    return res

