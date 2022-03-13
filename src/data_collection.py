from utils.utils import scrape_band

import pickle

url = "https://www.tekstowo.pl/piosenki_artysty,akcent_pl_.html"


res = scrape_band(url)

# saving the results
#with open("../songs_akcent", "wb") as handle:
#    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)












