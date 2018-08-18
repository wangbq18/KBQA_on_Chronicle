import pandas as pd

df = pd.read_csv('./place_name.csv')
title = df['place_name'].values

with open('./place_name.txt', 'a') as f:
    for t in title[1:]:
        f.write(t + ' ' + 'ns' + '\n')
