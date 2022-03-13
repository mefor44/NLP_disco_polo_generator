import requests
from bs4 import BeautifulSoup


def scrape_text(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    tab = soup.findAll("div", attrs={"class":"inner-text"})
    return tab[0].text


def scrape_band(url, verbose=True):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    pages = [i.contents[0] for i in soup.findAll("a", attrs={"class": "page-link"})]
    page_nums = []
    for i in pages:
        try:
            page_nums.append(int(i))
        except ValueError:
            continue

    max_page_num = max(page_nums)

    active = soup.find("li", attrs={"class": "page-item active"})
    active_page_num = int(active.find("a").contents[0])

    res = []

    # collect data for each page with music hits
    while active_page_num <= max_page_num:

        # collect all metadata
        tables = soup.findAll("div", attrs={"class": "ranking-lista"})
        tables = tables[0].findAll("a", attrs={"class": "title"})
        metadata = [(elem.get("title"), elem.get("href")) for elem in tables]

        # collect song texts
        for i, (title, link_end) in enumerate(metadata):
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

