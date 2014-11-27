GenrePredictor
==============

This project aims to utilize various machine learning techniques in order to predict the genre of songs as accurately as possible

To run the data collector and organizer:
----------------------------------------
The data collector relies on parsing an aggregated h5 song file.
I already ran the code that aggregates this file. It is too big to put in Github and email, so I am putting it on Google Drive and distributing it to you guys that way for now. You need to get this file in order to parse the data.
It is called agg_all_songs.h5

There are some Python libraries that you will need to run the code. The easiest way to get them is probably pip. There are usually instructions you can look up online if you have trouble downloading them. They are:
-tables
  +This is a library for reading hdf5 files
-sqlite3
  +python might actually come with this
-numpy
-Not sure what else you would need to install, but if the code fails due to a library, then it should say which one, and just install it

The file that has everything you need to get a list of Datapoints is datacollector.py
This file relies on Artistdata.py to use the custom dictionary named Datapoint as well as hdf5_getters.py which is used to retreive data from the h5 song file.

In the main function of datacollector.py I have code written that shows how to use this class in order to parse the data and get a list of Datapoints. Line 556-559 call get_mbtag_freq() to get the top 100 most frequent tags used in the DB and then makes an inverted index out if it. Line 583 calls parse_aggregate_songs with the aggregate file I will share on Google Drive that creates an intermediate map of just straight reading the song data and maps all of the song data to particular artists. Line 585 calls parse_artis_map() using the map just created and the tag frequency inverted index in order to flatten out all list values in this map, just using simple averaging at the moment. This creates a list of flattened maps. Finally, on line 587 scale_and_convert_maps() takes the list of flattened artist maps you just created and scales all of the non-binary features to values between 0.0-1.0 (besides the years) and then converts these maps to the Datapoint class (literarlly just a dictionary with instance variables) and adds them to a new list which gets returned by this function. This is the final list you should be working with. I have a lot of notes in the file too that are generally for myself to make some updates in the future. This should still be enough to get going. I have this code in the main function now, but you can just import this class to run the functions similarly to how I do in the main function to get a list of Datapoint maps.
