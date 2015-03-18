from auth import get_authed_api
from pprint import pprint

import sys, json, os.path, datetime, dateutil.relativedelta, math, string, gmusicapi

class DataManager:
    def __init__(self, api = False): 
        self.cache_dir = 'cache/'
        self.artists_json_file = self.cache_dir + 'artists.json'
        self.library_songs_json_file = self.cache_dir + 'library_songs.json'
        self.artists_songs_json_file_format = self.cache_dir + 'artist_{}_{}_songs.json'
        self.songs_listened_to_json_file = self.cache_dir + 'songs_listened_to.json'

        self.api = False
        if api:
            self.load_api()

    def load_api(self):
        self.api = get_authed_api()
        if self.api:
            print("Authenticated. API Ready!")

    def get_all_my_data(self, force_reload_cache = False):
        # Initialize our return variables
        artists = {}
        library_songs = {}

        # Use cached data if available
        if not force_reload_cache or not self.api:
            if os.path.isfile(self.artists_json_file):
                print("Loading Artists from cache...")
                artists_file = open(self.artists_json_file, 'r')
                artists = json.loads(artists_file.read())
                artists_file.close()
            if os.path.isfile(self.library_songs_json_file):
                print("Loading Songs in Library from cache...")
                library_songs_file = open(self.library_songs_json_file, 'r')
                library_songs = json.loads(library_songs_file.read())
                library_songs_file.close()

        # If we have acces to the API, lets get new data
        if self.api and len(artists) == 0 and len(library_songs) == 0:
            print("Retrieving Songs in Library from API...")
            library_songs = self.api.get_all_songs()
            print("Extracting Artists from Songs in Library data...")
            for song in library_songs:
                if 'artistId' in song:
                    for artist in song['artistId']:
                        if artist not in artists:
                            artists[artist] = {'name': song['artist'], 'library_songs': [song]}
                        else:
                            artists[artist]['library_songs'].append(song)

            # Build the cache
            print("Caching Artists...")
            artists_file = open(self.artists_json_file, 'w')
            artists_file.write(json.dumps(artists, indent=2))
            artists_file.close()
            print("Caching Songs in Library...")
            library_songs_file = open(self.library_songs_json_file, 'w')
            library_songs_file.write(json.dumps(library_songs, indent=2))
            library_songs_file.close()

        return artists, library_songs

    def get_songs_by_artist(self, artist_id, name, force_reload_cache = False):
        # Initialize our return variables
        songs = {}

        # Use cached data if available
        artist_slug = self.strip_unicode(name).strip().lower().replace(' ', '-')
        artist_slug = ''.join(c for c in artist_slug if c in ('-_.' + string.ascii_letters + string.digits))
        artists_songs_json_file = self.artists_songs_json_file_format.format(artist_id, artist_slug)
        if not force_reload_cache or not self.api:
            if os.path.isfile(artists_songs_json_file):
                print("Loading Songs for Artist '{}' from cache...".format(name))
                artists_songs_file = open(artists_songs_json_file, 'r')
                songs = json.loads(artists_songs_file.read())
                artists_songs_file.close()
                return songs

        # If we have access to the API, lets get new data
        if self.api and len(songs) == 0:
            try: 
                print("Retrieving info for Artist '{}' from API...".format(name))
                info = self.api.get_artist_info(artist_id, False, 10000, 0)
            except: 
                print("!! Failed to retrieve information for Artist '{}'".format(name))
                return songs
            if 'topTracks' in info:
                for song in info['topTracks']:
                    songs[song['nid']] = song

            # Build the cache
            print("Building Song cache for Artist '{}'".format(name))
            artists_songs_file = open(artists_songs_json_file, 'w')
            artists_songs_file.write(json.dumps(songs, indent=2))
            artists_songs_file.close()

        return songs

    def get_songs_listened_to(self, force_reload_cache = False, force_reload_artist_cache = False):
        # Initialize our return variables
        songs = {}

        # Use cached data if possible
        if not force_reload_cache or not self.api:
            if os.path.isfile(self.songs_listened_to_json_file):
                print("Loading Songs Listened To from cache...")
                songs_listened_to_file = open(self.songs_listened_to_json_file, 'r')
                songs = json.loads(songs_listened_to_file.read())
                songs_listened_to_file.close()
                return songs

        # pull data from api
        if self.api and len(songs) == 0:
            def addsong(song, artist = ""):
                if 'artist' in song and artist == "":
                    artist = song['artist']
                artistname = self.strip_unicode(artist)
                title = self.strip_unicode(song['title'])
                key = title + " by " + artistname
                song[u'totalListenedMillis'] = song['playCount'] * float(song['durationMillis'])
                if key in songs:
                    songs[key]['playCount'] += song['playCount']
                songs[key] = song

            print("Building Songs Listened To dataset...")
            [artists, library_songs] = self.get_all_my_data(force_reload_cache)
            for song in library_songs:
                if 'playCount' not in song: 
                    continue
                if song['playCount'] < 1:
                    continue
                addsong(song)
            for artist in artists:
                artistname = self.strip_unicode(artists[artist]['name'])
                artist_songs = {}
                try:
                    artist_songs = self.get_songs_by_artist(artist, artistname, force_reload_artist_cache)
                except gmusicapi.exceptions.ValidationException as e:
                    print("Hiccup!")
                artists[artist]['songs'] = artist_songs
                for song in artist_songs:
                    s = artist_songs[song]
                    if 'playCount' not in s: 
                        continue
                    if s['playCount'] < 1:
                        continue
                    addsong(s)

            # Buld the cache
            print("Saving Songs Listened To dataset to cache...")
            songs_listened_to_file = open(self.songs_listened_to_json_file, 'w')
            songs_listened_to_file.write(json.dumps(songs, indent=2))
            songs_listened_to_file.close()

        print("Total Songs Listened To: {}".format(len(songs)))

        return songs

    def timeperiod(self, seconds):
        dt1 = datetime.datetime.fromtimestamp(0)
        dt2 = datetime.datetime.fromtimestamp(seconds)
        rd = dateutil.relativedelta.relativedelta(dt2, dt1)

        return "{0}d {1:02d}:{2:02d}:{3:02d}".format(rd.days + (rd.months * 30) + (rd.years * 365), rd.hours, rd.minutes, rd.seconds)

    def print_data(self, song, primary_field, title, i = None): 
        title = self.strip_unicode(title).strip()
        totalSeconds = math.floor(song['totalListenedMillis'] / 1000)
        plays = song['playCount']
        duration = ""
        if 'durationMillis' in song:
            durationSeconds = (float(song['durationMillis']) / 1000)
            mins = int(math.floor(durationSeconds / 60))
            secs = int(durationSeconds % 60)
            duration = "{0:02d}:{1:02d}".format(mins, secs)
        base_fmt = "{1} | {2}"
        if i != None:
            base_fmt = "  {0}. " + base_fmt
        if 'durationMillis' in song:
            base_fmt += " | {3}"
        print(base_fmt.format(i, primary_field, title, duration))

    def strip_unicode(self, s):
        return ''.join([j if ord(j) < 128 else '' for j in s])

if __name__ == "__main__":
    # Manually add the new fields for our script for the API's format
    # expectation
    #ne = gmusicapi.protocol.metadata.Expectation("lastRatingChangeTimestamp", "string", False, True, True)
    #gmusicapi.protocol.metadata.md_expectations[ne.name] = ne

    # Force cache rebuild
    data = DataManager(api=True)
    data.get_songs_listened_to(True, False)

