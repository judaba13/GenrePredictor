import os
import sys
import glob
import string
import time
import datetime
import operator
import math
import sys
import numpy as np
from Artistdata import *
import hdf5_getters
import nb
import pickle
try:
    import sqlite3 as db
except ImportError:
    print 'please install sqlite3 to use this'
    sys.exit(0)

"""
for d in data: # datapoint d, data as a list of Datapoint
    for feature in d: # feature is feature name as string / key in dict
        # do stuff with the feature/value pair
        # d[feature] is value as float 

"""

def die_with_usage():
    """ HELP MENU """
    print 'datacollector.py'
    print ''
    print 'usage:'
    print '   python datacollector.py track_metadata.db output.txt'
    print 'creates a file where each line is: (one line per artist)'
    print 'artist id,artist mbid,track id,artist name'
    sys.exit(0)

def get_stuff():
    """
    Just a test function to see if I can query the DBs
    """
    result = []
    #con = db.connect('subset_artist_similarity.db')
    #con = db.connect('subset_artist_term.db')
    con = db.connect('subset_track_metadata.db')
    cur = con.cursor()   
    cur.execute('SELECT * FROM sqlite_master WHERE type = "table"')
    for row in cur.fetchall():
        result.append(row)
    return result

def get_artist_details(artist_ids):
    """
    Given a list of artist ids, gets all details pertaining to the artist
    """
    con = None
    result = []
    try:
        con = db.connect('subset_track_metadata.db')
        cur = con.cursor()

        # also attach artist terms
        cur.execute('ATTACH ? as artist_term_db', ('subset_artist_term.db',) )


        for artist_id in artist_ids:
            new_record = {'artist_id':artist_id}

            # note that artist the max familiarity may be higher here...
            cur.execute('SELECT min(year), max(year), min(artist_familiarity), max(artist_familiarity), min(artist_hotttnesss), max(artist_hotttnesss) FROM songs WHERE artist_id = ? AND year > 0 LIMIT 1', (artist_id,))
            row = cur.fetchone()
            # hack for when the artist has no years for any songs (we skip that artist)
            if row[0] is None: continue
            new_record['year_first_song'] = row[0]
            new_record['year_last_song'] = row[1]
            new_record['artist_familiarity_min'] = row[2]
            new_record['artist_familiarity_max'] = row[3]
            new_record['artist_hotttnesss_min'] = row[4]
            new_record['artist_hotttnesss_max'] = row[5]
            
            # get the best artist name as the most common
            cur.execute('SELECT artist_name, COUNT(*) as `num` FROM songs WHERE artist_id = ? GROUP BY artist_name ORDER BY num DESC', (artist_id,))
            row = cur.fetchone()
            new_record['artist_name'] = row[0]
            # also list the rest of the artist names? (could set limit to one otherwise)
            include_other_names = False
            if include_other_names:
                all_artist_names = []
                for row in cur.fetchall():
                    all_artist_names.append(row[0])
                new_record['other_artist_names'] = all_artist_names

            # get a sample of songs
            top_songs_each_year = True
            if top_songs_each_year:
                year_min = new_record['year_first_song']
                year_max = new_record['year_last_song']
                song_list = []
                for year in range(year_min, year_max+1):
                    songs = get_songs(artist_id, year, year, 1)
                    if len(songs) == 1: song_list.append(songs[0])
                new_record['top_songs'] = song_list
            else:
                early_song = get_songs(artist_id, new_record['year_first_song'], new_record['year_first_song'] + 1, 1)
                if (len(early_song) == 1):
                    early_song = early_song[0]
                else:
                    early_song = None
                
                middle_song = get_songs(artist_id, new_record['year_first_song'] + 1, new_record['year_last_song'] - 1, 1)
                if (len(middle_song) == 1):
                    middle_song = middle_song[0]
                    if (middle_song == early_song):
                            middle_song = None
                else:
                    middle_song = None

                late_song = get_songs(artist_id, new_record['year_last_song'] - 1, new_record['year_last_song'], 1)
                if (len(late_song) == 1):
                    late_song = late_song[0]
                    if (middle_song == late_song or early_song == late_song):
                            late_song = None

                else:
                    late_song = None

                new_record['top_songs'] = [early_song, middle_song, late_song]

            # get terms
            cur.execute('SELECT term FROM artist_term WHERE artist_term.artist_id = ?', (artist_id,))
            terms = []
            for row in cur.fetchall():
                terms.append(row[0])
            new_record['terms'] = terms
            
            result.append(new_record)

    except db.Error, e:
        result.append("Error %s:" % e.args[0])
    finally:
        if con:
            con.close()
    return result

def get_artists(year_min, year_max, limit, order_by = None):
    """
    Gets artists and their details withing a year range
    """
    con = None
    result = []
    try:
        #con = db.connect('subset_artist_similarity.db')
        #con = db.connect('subset_artist_term.db')
        con = db.connect('subset_track_metadata.db')
        cur = con.cursor()   

        # get the artist ids
        core_query = 'SELECT distinct artist_id FROM songs WHERE year BETWEEN ? AND ? %s LIMIT ?'
        if order_by is None or order_by == 'artist_familiarity':
            query = core_query % 'ORDER BY artist_familiarity DESC'
        elif order_by == 'artist_hotttnesss':
            query = core_query % 'ORDER BY artist_hotttnesss DESC'
        else:
            raise Exception("unexpected order_by")
        cur.execute(query, (year_min, year_max, limit))
        artist_ids = [row[0] for row in cur.fetchall()]
        return get_artist_details(artist_ids)

    except db.Error, e:
        result.append("Error %s:" % e.args[0])
    finally:
        if con:
            con.close()
    return ['unexpected end of function']

def get_songs(artist_id, year_min, year_max, limit):
    """
    Gets songs for a particular artist between given years
    """
    con = None
    try:
        #con = db.connect('subset_artist_similarity.db')
        #con = db.connect('subset_artist_term.db')
        con = db.connect('subset_track_metadata.db')
        cur = con.cursor()   

        #cur.execute('SELECT artist_id, artist_name, title, year, track_7digitalid FROM songs WHERE artist_id = ? AND year BETWEEN ? AND ? ORDER BY artist_familiarity DESC LIMIT ?', (artist_id, year_min, year_max, limit))
        cur.execute('SELECT artist_id, artist_name, title, year, track_id, duration FROM songs WHERE artist_id = ? AND year BETWEEN ? AND ? ORDER BY year ASC LIMIT ?', (artist_id, year_min, year_max, limit))
        result = []
        for row in cur.fetchall():
            new_record = {}
            new_record['artist_id'] = row[0]
            new_record['artist_name'] = row[1]
            new_record['title'] = row[2]
            new_record['year'] = row[3]
            new_record['track_id'] = row[4]
            new_record['duration'] = row[5]
            result.append(new_record)
        return result

    except db.Error, e:
        return [("Error %s:" % e.args[0])]
    finally:
        if con:
            con.close()
    return ['unexpected end of function']

def get_mbtag_freq(n, tags):
    """
    Gets the n most popular mbtags for artists in the db
    tags true means use the mbtags else use econest terms
    NOTE: ECONEST seems to give better terms
    """
    con = None
    try:
        con = db.connect('subset_artist_term.db')
        c = con.cursor()
        table = 'artist_mbtag' if tags else 'artist_term'
        q = "SELECT * FROM %s" % table

        res = c.execute(q)
        res = res.fetchall()
        tag_freq_map = {}
        for pair in res:
            term = pair[1]
            if term in tag_freq_map:
                tag_freq_map[term] += 1
            else:
                tag_freq_map[term] = 1

        #sort the frequency map by value
        sorted_freq = sorted(tag_freq_map.items(), key=operator.itemgetter(1))
        #print len(sorted_freq)
        return sorted_freq[-n:]
        
        #return sorted(tag_freq_map.values())
    except db.Error, e:
        return [("Error %s:" % e.args[0])]
    finally:
        if con:
            con.close()
    return ['unexpected end of function']


def parse_aggregate_songs(file_name):
    """
    Given an aggregate filename and artist_map in the format
    {artist_name: {data pertaining to artist}}
    """
    """
    TODO: 
    -this function goes through each song, if artist not in there,
    add all data necesary and add first song info.
    else update any specific song info

    -song info is a map from attributename:[values]
    """
    artist_map = {}
    h5 = hdf5_getters.open_h5_file_read(file_name)
    numSongs = hdf5_getters.get_num_songs(h5)
    print 'Parsing song file...'
    for i in range(numSongs):
        artist_name = hdf5_getters.get_artist_name(h5,i)

        #Filter location
        longi = hdf5_getters.get_artist_longitude(h5,i)
        lat = hdf5_getters.get_artist_latitude(h5,i)
        loc = hdf5_getters.get_artist_location(h5,i)
        if math.isnan(lat) or math.isnan(longi):
            #skip if no location
            continue

        #filter year
        yr = hdf5_getters.get_year(h5,i)
        if yr == 0:
            #skip if no year
            continue

        #filter hotttness and familiarity
        familiarity = hdf5_getters.get_artist_familiarity(h5,i)
        hotttness = hdf5_getters.get_artist_hotttnesss(h5,i)
        if familiarity<=0.0 or hotttness<=0.0:
            #skip if no hotttness or familiarity computations
            continue

        #TODO:MAYBE filter on dance and energy
        timbre = hdf5_getters.get_segments_timbre(h5,i)
        #timbre[#] gives len 12 array so for each arr in timbre, add up to get segment and add to corresponding 12 features and avg across each
        if not artist_name in artist_map:
            #have not encountered the artist yet, so populate new map
            sub_map = {}
            sub_map['analysis_sample_rate'] = [hdf5_getters.get_analysis_sample_rate(h5,i)]
            sub_map['artist_familiarity'] = familiarity
            sub_map['artist_hotttnesss'] = hotttness
            sub_map['artist_id'] = hdf5_getters.get_artist_id(h5,i)
            #longi = hdf5_getters.get_artist_longitude(h5,i)
            #lat = hdf5_getters.get_artist_latitude(h5,i)
            #longi = None if math.isnan(longi) else longi
            #lat = None if math.isnan(lat) else lat
            sub_map['artist_latitude'] = lat
            sub_map['artist_longitude'] = longi
            sub_map['artist_location'] = loc
            sub_map['artist_terms'] = hdf5_getters.get_artist_terms(h5,i)
            #TODO:see if should weight by freq or weight for if the term matches one of the feature terms
            sub_map['artist_terms_freq'] = list(hdf5_getters.get_artist_terms_freq(h5,i))
            sub_map['artist_terms_weight'] = list(hdf5_getters.get_artist_terms_weight(h5,i))

            #song-sepcific data
            #TODO COMPUTE AN AVG TIMBRE FOR A SONG BY IDEA:
            #SUMMING DOWN EACH 12 VECTOR FOR EACH PT IN SONG AND AVG THIS ACROSS SONG
            dance = hdf5_getters.get_danceability(h5,i)
            dance = None if dance == 0.0 else dance
            energy = hdf5_getters.get_energy(h5,i)
            energy = None if energy == 0.0 else energy
            sub_map['danceability'] = [dance]
            sub_map['duration'] = [hdf5_getters.get_duration(h5,i)]
            sub_map['end_of_fade_in'] = [hdf5_getters.get_end_of_fade_in(h5,i)]
            sub_map['energy'] = [energy]
            #since each song has a key, ask if feature for keys should be num of songs that appear in that key or
            #just binary if any of their songs has that key or just be avg of songs with that key
            #same for mode, since its either major or minor...should it be count or avg.?
            sub_map['key'] = [hdf5_getters.get_key(h5,i)]
            sub_map['loudness'] = [hdf5_getters.get_loudness(h5,i)]
            sub_map['mode'] = [hdf5_getters.get_mode(h5,i)] #major or minor 0/1
            s_hot = hdf5_getters.get_song_hotttnesss(h5,i)
            s_hot = None if math.isnan(s_hot) else s_hot
            sub_map['song_hotttnesss'] = [s_hot]
            sub_map['start_of_fade_out'] = [hdf5_getters.get_start_of_fade_out(h5,i)]
            sub_map['tempo'] = [hdf5_getters.get_tempo(h5,i)]
            #should time signature be count as well? binary?
            sub_map['time_signature'] = [hdf5_getters.get_time_signature(h5,i)]
            sub_map['track_id'] = [hdf5_getters.get_track_id(h5,i)]
            #should year be binary since they can have many songs across years and should it be year:count
            sub_map['year'] = [yr]

            artist_map[artist_name] = sub_map
        else:
            #artist already exists, so get its map and update song fields
            dance = hdf5_getters.get_danceability(h5,i)
            dance = None if dance == 0.0 else dance
            energy = hdf5_getters.get_energy(h5,i)
            energy = None if energy == 0.0 else energy
            artist_map[artist_name]['analysis_sample_rate'].append(hdf5_getters.get_analysis_sample_rate(h5,i))
            artist_map[artist_name]['danceability'].append(dance)
            artist_map[artist_name]['duration'].append(hdf5_getters.get_duration(h5,i))
            artist_map[artist_name]['end_of_fade_in'].append(hdf5_getters.get_end_of_fade_in(h5,i))
            artist_map[artist_name]['energy'].append(energy)
            artist_map[artist_name]['key'].append(hdf5_getters.get_key(h5,i))
            artist_map[artist_name]['loudness'].append(hdf5_getters.get_loudness(h5,i))
            artist_map[artist_name]['mode'].append(hdf5_getters.get_mode(h5,i)) #major or minor 0/1
            s_hot = hdf5_getters.get_song_hotttnesss(h5,i)
            s_hot = None if math.isnan(s_hot) else s_hot
            artist_map[artist_name]['song_hotttnesss'].append(s_hot)
            artist_map[artist_name]['start_of_fade_out'].append(hdf5_getters.get_start_of_fade_out(h5,i))
            artist_map[artist_name]['tempo'].append(hdf5_getters.get_tempo(h5,i))
            #should time signature be count as well? binary?
            artist_map[artist_name]['time_signature'].append(hdf5_getters.get_time_signature(h5,i))
            artist_map[artist_name]['track_id'].append(hdf5_getters.get_track_id(h5,i))
            #should year be binary since they can have many songs across years and should it be year:count
            artist_map[artist_name]['year'].append(yr)
    return artist_map

def compute_avg(lst):
    """
    Computes the avg of a list only taking into account values that aren't None
    """
    #TODO: make it return none if result is 0.0
    lst_sum = 0.0
    not_none_total = 0.0
    for i in lst:
        if i:
            lst_sum += i
            not_none_total += 1.0
    if not_none_total == 0.0 or lst_sum == 0.0:
        return 0.0
    else:
        return lst_sum / not_none_total

#global variables that will be used to scale features
analysis_sample_rate_min=artist_longitude_min=artist_latitude_min=duration_min=end_of_fade_in_min=loudness_min=start_of_fade_out_min=tempo_min = sys.float_info.max
analysis_sample_rate_max=artist_longitude_max=artist_latitude_max=duration_max=end_of_fade_in_max=loudness_max=start_of_fade_out_max=tempo_max= sys.float_info.min

def parse_artist_map(artist_map, term_freq):
    """
    Parses the artists map that is generated from a song file into
    the Datapoint class, which is just a map.
    Takes in a map of terms:freq for the top terms associated with artists to be made into binary features
    Takes care of flattening features such as song features
    """
    global analysis_sample_rate_min,artist_longitude_min,artist_latitude_min,duration_min,end_of_fade_in_min,loudness_min,start_of_fade_out_min,tempo_min,analysis_sample_rate_max,artist_longitude_max,artist_latitude_max,duration_max,end_of_fade_in_max,loudness_max,start_of_fade_out_max,tempo_max
    artist_list = []
    print "Flattening artist map"
    for artist in artist_map:
        flattened_artist_map = {}
        flattened_artist_map['artist_name'] = artist
        a_map = artist_map[artist]
        for feature in a_map:
            #goes through each feature and extracts it properly
            if feature == 'analysis_sample_rate':
                sr = compute_avg(a_map[feature])
                if sr < analysis_sample_rate_min:
                    analysis_sample_rate_min = sr
                if sr > analysis_sample_rate_max:
                    analysis_sample_rate_max = sr
                flattened_artist_map['analysis_sample_rate'] = sr
            elif feature == 'artist_familiarity':
                flattened_artist_map['artist_familiarity'] = a_map[feature]
            elif feature == 'artist_hotttnesss':
                flattened_artist_map['artist_hotttnesss'] = a_map[feature]
            elif feature == 'artist_id':
                flattened_artist_map['artist_id'] = a_map[feature]
            elif feature == 'artist_latitude':
                lat = a_map[feature]
                if lat and lat < artist_latitude_min:
                    artist_latitude_min = lat
                if lat > artist_latitude_max:
                    artist_latitude_max = lat
                flattened_artist_map['artist_latitude'] = lat
            elif feature == 'artist_longitude':
                lng = a_map[feature]
                if lng and lng < artist_longitude_min:
                    artist_latitude_min = lng
                if lng > artist_longitude_max:
                    artist_longitude_max = lng
                flattened_artist_map['artist_longitude'] = lng
            elif feature == 'artist_location':
                flattened_artist_map['artist_location'] = a_map[feature]
            elif feature == 'artist_terms':
                for popular_term in term_freq:
                    #make a feature for each popular term
                    include_term = 1.0 if popular_term in a_map[feature] else 0.0
                    flattened_artist_map['b_'+popular_term] = include_term
                    #TODO: WEIGHT IT BY FREQ OR WEIGHT???
            elif feature == 'danceability':
                #TODO: if compute_avg is 0.0, then make it none
                flattened_artist_map['danceability'] = compute_avg(a_map[feature])
            elif feature == 'duration':
                dur = compute_avg(a_map[feature])
                if dur<duration_min:
                    duration_min = dur
                if dur>duration_max:
                    duration_max =  dur
                flattened_artist_map['duration'] = dur
            elif feature == 'end_of_fade_in':
                fi = compute_avg(a_map[feature])
                if fi<end_of_fade_in_min:
                    end_of_fade_in_min=fi
                if fi>end_of_fade_in_max:
                    end_of_fade_in_max=fi
                flattened_artist_map['end_of_fade_in'] = fi
            elif feature == 'energy':
                #TODO: make none
                flattened_artist_map['energy'] = compute_avg(a_map[feature])
            elif feature == 'key':
                keys = a_map[feature]
                num_songs = len(keys)
                for k in range(12):
                    count = 0
                    for i in keys:
                        if k == i:
                            count += 1
                    flattened_artist_map['key_'+str(k)] = (1.0*count)/num_songs
            elif feature == 'loudness':
                ld = compute_avg(a_map[feature])
                if ld<loudness_min:
                    loudness_min=ld
                if ld>loudness_max:
                    loudness_max=ld
                flattened_artist_map['loudness'] = ld
            elif feature == 'mode':
                modes = a_map[feature]
                num_songs = len(modes)
                for m in range(2):
                    count = 0
                    for i in modes:
                        if i == m:
                            count += 1
                    flattened_artist_map['mode_'+str(m)] = (1.0*count)/num_songs
            elif feature == 'song_hotttnesss':
                #TODO make none
                flattened_artist_map['song_hotttnesss'] = compute_avg(a_map[feature])
            elif feature == 'start_of_fade_out':
                fo = compute_avg(a_map[feature])
                if fo<start_of_fade_out_min:
                    start_of_fade_out_min=fo
                if fo>start_of_fade_out_max:
                    start_of_fade_out_max=fo
                flattened_artist_map['start_of_fade_out'] = fo
            elif feature == 'tempo':
                tp = compute_avg(a_map[feature])
                if tp<tempo_min:
                    tempo_min=tp
                if tp>tempo_max:
                    tempo_max=tp
                flattened_artist_map['tempo'] = tp
            elif feature == 'time_signature':
                sigs = a_map[feature]
                num_songs = len(sigs)
                for t in range(3,8):
                    count = 0
                    for s in sigs:
                        if s == t:
                            count += 1
                    flattened_artist_map['time_signature_'+str(t)] = (1.0*count)/num_songs
            elif feature == 'track_id':
                flattened_artist_map['track_id'] = a_map[feature]
            elif feature == 'year':
                #min, max and avg year
                yrs = a_map[feature]
                min_val = 10000
                for yr in yrs:
                    if yr < min_val and yr != 0:
                        min_val = yr
                min_val = min_val if min_val != 10000 else 0
                max_val = max(yrs)
                avg_val = compute_avg(yrs)
                flattened_artist_map['years'] = yrs
                flattened_artist_map['y_max_year'] = max_val
                flattened_artist_map['y_min_year'] = min_val
                flattened_artist_map['y_avg_year'] = avg_val
        artist_list.append(flattened_artist_map)
    return artist_list

def scale(old_val,old_min,old_max):
    """
    Given a range of possible values, scales an old_val
    to be between 0.0 and 1.0
    """
    if not old_val:
        #if no value supplied default to 0.0?
        return 0.0
    new_max = 1.0
    new_min = 0.0
    old_range = old_max - old_min
    if old_range == 0:
        new_val = new_min
    else:
        new_range = new_max - new_min
        new_val = (((old_val - old_min) * new_range) / old_range) + new_min
    return new_val

def scale_and_convert_maps(artist_maps):
    """
    Given a list of flattened versions of the artist_maps,
    scales all continuous attributes to be in the range 0.0-1.0
    and converts the maps to the Datapoint class
    """
    data_points = [] #the final list of Datapoint maps
    for artist_map in artist_maps:
        #for each map, scale the values needed to be scaled
        #then convert it to Datapoint and append it to list
        artist_map['analysis_sample_rate'] = scale(artist_map['analysis_sample_rate'],analysis_sample_rate_min,analysis_sample_rate_max)
        artist_map['artist_longitude'] = scale(artist_map['artist_longitude'],artist_longitude_min,artist_longitude_max)
        artist_map['artist_latitude'] = scale(artist_map['artist_latitude'],artist_latitude_min,artist_latitude_max)
        artist_map['duration'] = scale(artist_map['duration'],duration_min,duration_max)
        artist_map['end_of_fade_in'] = scale(artist_map['end_of_fade_in'],end_of_fade_in_min,end_of_fade_in_max)
        artist_map['loudness'] = scale(artist_map['loudness'],loudness_min,loudness_max)
        artist_map['start_of_fade_out'] = scale(artist_map['start_of_fade_out'],start_of_fade_out_min,start_of_fade_out_max)
        artist_map['tempo'] = scale(artist_map['tempo'],tempo_min,tempo_max)

        #convert each artist map into a Datapoint and add it to list
        datapt = DataPoint(artist_map)
        data_points.append(datapt)

    return data_points

def generate_data():
    """
    This is the master function to call that returns a list of Datapoints!
    """
    #Gets the most popular artist tags
    res = get_mbtag_freq(100, False) #use top 100 results for genres [eco name:0/1] in feature map
    freq_map = {}
    for pair in res:
        freq_map[pair[0]] = pair[1]

    #Takes an aggregated song file (created from create_summary_file.py) and parses it
    artist_map = parse_aggregate_songs('agg_all_songs.h5')
    #flattens the artist map into a list
    artist_list = parse_artist_map(artist_map, freq_map)
    #normalize the list and make it a list of Datapoints
    data = scale_and_convert_maps(artist_list)
    return data

if __name__ == '__main__':
    """
    table_res = get_stuff()
    print table_res
    """
    #TODO: SCALE ALL VALUES THAT ARENT ALREADY BETWEEN 0-1 to be between 0.0-1.0 depending on max and min value for those features
    #TODO: Number of tracks as a feature
    #TODO: MAKE KEY 0-11 FEATURES WITH VALUE OF COUNT/NUMSONGS that ARENT 0
    #WHEN AVGING, MAKE SURE TO ONLY INCLUDE ONES THAT ARENT NONE
    #print os.path.isfile('MillionSongSubset\\data\\A\\M\\B\\TRAMBNF128F426FBB6.h5')
    #h5 = hdf5_getters.open_h5_file_read('MillionSongSubset\\data\\A\\P\\X\\TRAPXOE128F92FAB15.h5')
    #a = np.array(hdf5_getters.get_artist_terms(h5))
    #print a
    
    #artist_info = get_artists(1900, 2020, 1000000)
    #print artist_info[1079]

    """
    #Gets the most popular artist tags
    res = get_mbtag_freq(100, False) #use top 100 results for genres [eco name:0/1] in feature map
    freq_map = {}
    for pair in res:
        freq_map[pair[0]] = pair[1]

    #can compare unicode to normal string
    #TODO: LOOK UP GMAP API TO CONVERT LOCATION TO LONG/LAT
    #If no location, find way to look up artist location to fill in
    #TODO: when parsing map pass in the term freq map too to get top terms to use as features
    #TODO: Should time signature be binary? look up max and min of time signature!
    #map nan log/lat to None
    #math.isnan(#)
    #make key binary 0-11
    #for confidences either ignore or wieght it by that
    #keep DB id as field
    """
    """
    NOTE:  term frequency is directly proportional to how often that term
    is used to describe that artist. Term weight is a measure of how 
    important that term is in describing the artist. As an example of the
    difference, the term 'rock' may be the most frequently applied term for
    The Beatles. However, 'rock' is not very descriptive since many bands
    have 'rock' as the most frequent term. However, the most highly 
    weighted terms for The Beatles are 'merseybeat' and 'british invasion', 
    which give you a better idea of what The Beatles are all about than 'rock' does. We don't publish the details of our algorithms, but I can tell you that frequency is related to the simple counting of appearance of a term, whereas weight is related to TF-IDF
    """
    """
    #Takes an aggregated song file (created from create_summary_file.py) and parses it
    artist_map = parse_aggregate_songs('agg_all_songs.h5')
    #flattens the artist map into a list
    artist_list = parse_artist_map(artist_map, freq_map)
    #normalize the list and make it a list of Datapoints
    data = scale_and_convert_maps(artist_list)
    #data holds a list of Datapoints (aka maps)
    """
    data = generate_data()
    #pickle stuff
    output = open('data.pkl','wb')
    pickle.dump(data,output)
    output.close()

    """
    print data2[15]
    print data2[15].hotttnesss
    print data2[15].familiarity
    print data2[15].artist_name
    print data2[15].artist_id
    print data2[15].artist_location==""
    print data2[15].track_ids[0]
    """
    
    
    
    """
    print str(len(data))
    print data[17]
    print data[17].years
    print data[17].hotttnesss
    print data[17].familiarity
    print data[17].artist_name
    print data[17].artist_id
    print data[17].artist_location==""
    print data[17].track_ids[0]
    """
    
    
    print 'Done parsing and flattening song file'