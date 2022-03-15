import pandas as pd
import pickle
import sys

from utils.utils import scrape_band, clean_record, Tee

#url = "https://www.tekstowo.pl/piosenki_artysty,akcent_pl_.html"
#res = scrape_band(url)


# for logging purposes
sys.stdout = Tee("log_data_collection.dat", mode="a")
# read the urls
urls = pd.read_excel("../data/Disco-Polo.xlsx")["link"]

n_bands = 0
n_hits = 0
with open("../data/songs_data", "a", encoding='utf-8') as file:
    # iterate over each band
    for band_url in urls:
        res = scrape_band(band_url, verbose=True, sleep_time=0.5)
        res_cleaned = [clean_record(txt) for txt in res]
        n_bands += 1
        n_hits += len(res_cleaned)
        # write output to the data file
        file.write(u'\n\n'.join(res_cleaned))

print(f"Data was scraped for {n_hits} songs.")
print(f"Data was scraped for {n_bands} bands.")











