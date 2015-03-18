from pprint import pprint
from data_manager import DataManager

import math, sys

top_n = 25
if len(sys.argv) > 1:
    top_n = int(sys.argv[1])

data = DataManager()
songs = data.get_songs_listened_to().items()

totalTime = 0
totalPlays = 0
for song in songs:
    totalPlays += song[1]['playCount']
    totalTime += song[1]['totalListenedMillis']

print("You have listened to {} tracks (of which {} are unique) worth a time span of {}.".format(totalPlays, len(songs), data.timeperiod(totalTime / 1000)))

