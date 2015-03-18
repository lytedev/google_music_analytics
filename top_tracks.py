from pprint import pprint
from data_manager import DataManager

import math, sys

top_n = 25
if len(sys.argv) > 1:
    top_n = int(sys.argv[1])

data = DataManager()
songs = data.get_songs_listened_to().items()
top_n = min(top_n, len(songs))

songs.sort(key=lambda x: x[1]['totalListenedMillis'], reverse=True)
print("Top Tracks by Time Listened")
for i in range(top_n):
    song = songs[i][1]
    data.print_data(song, data.timeperiod(song['totalListenedMillis'] / 1000), songs[i][0], i+1)
print("")

print("Top Tracks by Play Count")
songs.sort(key=lambda x: x[1]['playCount'], reverse=True)
for i in range(top_n):
    song = songs[i][1]
    data.print_data(song, song['playCount'], songs[i][0], i+1)
print("")

