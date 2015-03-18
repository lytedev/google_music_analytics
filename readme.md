# Google Music Analytics

A simple python script for those curious about their music listening habits.

## Dependencies

* Python 2.7
* `gmusicapi` module (`pip install gmusicapi`)

## Usage

Copy `auth.example.py` to `auth.py` and change the details inside to match your
own.

Run the `data_manager.py` script. This will cache all retrieved data as it runs for
analyses by other scripts.

Once you have the data, you're set! Write your own scripts to flip through the
data or run some of the scripts I've included and enjoy!

## Methodology

So if you flip through the code you'll wonder why I gather the data the way I
do. Hopefully an acceptable explanation follows. 

The function in the unofficial Google Music API I'm using retrieves only songs
_in our library_. This was a problem for me, as I use the Radio functionality a
good deal and even a vast majority of the songs I listen to are not actually in
my library. So I wasn't really able to retrieve "every song with at least 1
playCount". That would have made things really easy for doing what I wanted to
do. 

So I figured that, in my library, there is at least a song or two by almost every
_artist_ I listen to. So I could grab all the tracks in my library, then grab
all the tracks from those artists, then I probably had a pretty good subset of
data to analyze that was probably 95% complete. 

Still, if there was a way to just super-quick-like get every single song with
at least 1 playCount, that'd for sure be a better way to go. 

So, if you'd like this current iteration to be more accurate, be sure you have
at least one track by every artist you've listened to in your library. 

That said, if you have some 20,000 artists in your library, this could take a
long time to run - heck, you may even need more RAM! So maybe I should rewrite
the application to be more memory friendly at some point...

