import pickle

import pandas as pd

res = pd.read_pickle("../songs_akcent")

print(res[18])
print(len(res))


