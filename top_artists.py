from pprint import pprint
from data_manager import DataManager

import math, sys

top_n = 25
if len(sys.argv) > 1:
    top_n = int(sys.argv[1])

data = DataManager()
songs = data.get_songs_listened_to()

artist_data = {}
for s in songs:
    song = songs[s]
    artist = ''.join([j if ord(j) < 128 else '' for j in song['artist']]).strip()
    artist = artist.split('feat')[0].split(',')[0].strip()
    artist_key = artist.lower()
    if artist_key not in artist_data:
        artist_data[artist_key] = {u'playCount': 0, u'totalListenedMillis': 0, 'name': artist}

    artist_data[artist_key]['playCount'] += song['playCount']
    artist_data[artist_key]['totalListenedMillis'] += song['totalListenedMillis']

artist_data = artist_data.items()
top_n = min(top_n, len(artist_data))

artist_data.sort(key=lambda x: x[1]['totalListenedMillis'], reverse=True)
print("Top Artists by Total Listening Time")
for i in range(top_n):
    artist = artist_data[i][1]
    data.print_data(artist, data.timeperiod(artist['totalListenedMillis'] / 1000), artist_data[i][1]['name'], i+1)
print("")

artist_data.sort(key=lambda x: x[1]['playCount'], reverse=True)
print("Top Artists by Total Track Plays")
for i in range(top_n):
    artist = artist_data[i][1]
    data.print_data(artist, artist['playCount'], artist_data[i][1]['name'], i+1)
print("")





