import os
import sys
import glob
import string
import time
import datetime
import numpy as np
try:
    import sqlite3 as db
except ImportError:
    print 'please install sqlite3 to use this'
    sys.exit(0)

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

if __name__ == '__main__':
    """
    table_res = get_stuff()
    print table_res
    """
    #print os.path.isfile('MillionSongSubset\\data\\A\\M\\B\\TRAMBNF128F426FBB6.h5')

    artist_info = get_artists(1900, 2020, 1000000)
    print artist_info[100]


    """
    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output = sys.argv[2]

    # sanity check
    if not os.path.isfile(dbfile):
        print 'ERROR: can not find database:',dbfile
        sys.exit(0)
    if os.path.exists(output):
        print 'ERROR: file',output,'exists, delete or provide a new name'
        sys.exit(0)

    # start time
    t1 = time.time()

    # connect to the db
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    # get what we want
    q = 'SELECT artist_id,artist_mbid,track_id,artist_name FROM songs'
    q += ' GROUP BY artist_id  ORDER BY artist_id'
    res = c.execute(q)
    alldata = res.fetchall()
    # DEBUGGING
    q = 'SELECT DISTINCT artist_id FROM songs'
    res = c.execute(q)
    artists = res.fetchall()
    print 'found',len(artists),'distinct artists'
    assert len(alldata) == len(artists),'incoherent sizes'
    # close db connection
    c.close()
    conn.close()

    # write to file
    f = open(output,'w')
    for data in alldata:
        f.write(data[0]+','+data[1]+','+data[2]+',')
        f.write( data[3].encode('utf-8') + '\n' )
    f.close()

    # done
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'file',output,'with',len(alldata),'artists created in',stimelength
    """