#cdata.py

import json
import os
import urllib
import hashlib
import sqlite3
import requests
import gi
gi.require_version('Tracker', '3.0')
from gi.repository import GLib, Gio, Tracker
from . import pager
from .locals import local
from .dbase import db
from .previews import preview
from time import sleep
from webdav3.client import Client
from datetime import datetime
from pydbus import SessionBus
from pathlib import Path
from PIL import Image, ExifTags, TiffImagePlugin

cachepath = os.path.join(os.path.expanduser("~"), ".cache/pelican")

# con = sqlite3.connect(f"{cachepath}/pelican.db")

photosdir = os.path.join(os.path.expanduser("~"), "Pictures/Photos")

datetimerange = [None, None]
pages = []
proclock = False

curyear = 0
curdate = ''

def initdb():
    db3 = db(cachepath)
    if not db3.isInit():
        db3.initdb()

def addpreview():
    pass

def getlocation(lat, lon):
    """
    TODO: Move to local() object?
    """
    locurl = f"https://nominatim.openstreetmap.org/reverse?format=geocodejson&lat={lat}&lon={lon}"
    rloc = requests.get(locurl)
    locob = json.loads(rloc.text)
    print(locob)
    # check possible fields - they change with type of location
    # locality = locob['features'][0]['properties']['geocoding']['locality']
    """
    Might not have city. If not, use name (will be street name if type is highway) otherwise None
    If Key = tourism, get name
    """
    name = None
    if locob['features'][0]['properties']['geocoding']['osm_key'] == 'tourism':
        name = locob['features'][0]['properties']['geocoding']['name']
    town = None
    if locob['features'][0]['properties']['geocoding']['osm_key'] == 'highway' and 'city' not in locob['features'][0]['properties']['geocoding'].keys():
        name = locob['features'][0]['properties']['geocoding']['name']
    if 'city' in locob['features'][0]['properties']['geocoding'].keys():
        town = locob['features'][0]['properties']['geocoding']['city']
    
    state = locob['features'][0]['properties']['geocoding']['state']
    country = locob['features'][0]['properties']['geocoding']['country']

    return name, town, state, country

def updatephrase(photo_id, words):
    db3 = db(cachepath)
    curphrase = db3.getphrase(photo_id)
    print(curphrase)
    curwords = curphrase.split(' ') if curphrase != '' else []
    newwords = list(set(curwords + [w for w in words if None != w]))
    newphrase = ' '.join(newwords)
    res = db3.updatephrase(photo_id, newphrase)

    return res


def updatecache():
    db3 = db(cachepath)
    onlyfiles = []
    # onlyfiles = [f for f in os.listdir(photospath) if os.path.isfile(os.path.join(photospath, f))]
    """
    Need to paginate and loop: 100 picks/loop.
    Use LIMIT and OFFSET to create pages
    """
    try:
        connection = Tracker.SparqlConnection.bus_new(
            'org.freedesktop.Tracker3.Miner.Files',
            None, None)

        offset = 0
        new_pics = True
        while new_pics:

            stmt = connection.query_statement (
                f"""
                SELECT ?url ?typ
                WHERE {{
                        ?photo a nmm:Photo ;
                                nie:isStoredAs ?as .
                        ?as nie:url ?url .
                        ?photo nie:mimeType ?typ .
                        FILTER (?typ IN ('image/jpg', 'image/jpeg', 'image/raw' ) ) .
                        FILTER(regex(?url, "{photosdir}", "i" )) .
                
                }}
                LIMIT 100
                OFFSET {offset}
                """
                , None
            )
            # LIMIT 10
            cursor = stmt.execute()
            i = 0

            while cursor.next():
                """
                TODO: Redo this: create local() object first, then check that it exists based on hash not name.
                Flag name changes or moved files (same hash)
                """
                i += 1
                print('Result {0}: {1}'.format(i, cursor.get_string(0)[0]))
                uri = cursor.get_string(0)[0]
                file = uri.split('/')[-1]
                photospath = '/'.join(uri.replace('file://', '').split('/')[:-1])
                exists = db3.isphotoname(file)
                if not exists:
                    print('new')
                    newfile = local(photospath, file)
                    
                    # https://overpass-api.de/api/interpreter?data=[out:json];node[place~"^(village|town|city)$"](around:2500,44.05985555555556,5.130152777777778);out;
                    # place~"^(village|town|city)$"
                    # https://nominatim.openstreetmap.org/lookup?osm_ids=N26695231&format=json
                    lat, lon, alt, direction = newfile.getCoordinates()
                    # thumbbytes = newfile.getThumbnail()
                    rec = (
                        file, 
                        photospath,
                        newfile.getFileHash(), 
                        newfile.getCreatedDate(), 
                        newfile.getModel(), 
                        lat, 
                        lon, 
                        alt, 
                        direction
                    )
                    newid = db3.insertphoto(rec)
                    words = [file, newfile.getCreatedDate(), newfile.getModel()]
                    updatephrase(newid, words)
                    # iid = db.insert(newEntry)
                    
                    # img.save(f"{cachepath}/previews/{newid}", 'jpeg')

                    if lat and lon:
                        sleep(0.5)
                        name, town, state, country = getlocation(lat, lon)
                        ct = db3.addlocationtophoto(newid, name, town, state, country)
                        words = [name, town, state, country]
                        updatephrase(newid, words)

            print('A total of {0} results were found\n'.format(i))
            
            new_pics = True if i == 100 else False    
            offset += 100
            cursor.close()
        connection.close()

    except Exception as e:
        print('Error: {0}'.format(e))


    
    # saved = Query()
    
    


def get100pics(pagelist, direction = 'down', datelimit = None, qty = 100):
    # https://stackoverflow.com/questions/64661336/return-value-in-a-python-thread
    db3 = db(cachepath)
    picsrows = []
    if None == datelimit:
        datelimit = datetime.utcnow().isoformat()
    picsrows = db3.getpicspage(direction, datelimit, qty)
    # t = getToken('Google')
    
    for pic in picsrows:
        filename = pic[1]
        photospath = pic[2]

        print(photospath, filename)
        # realpic = local(photospath, filename)
        if os.path.isfile(os.path.join(photospath, filename)):
            # Preview = preview(pic[0], pic[1], pic[2], pic[3], pic[4], pic[5])
            pagelist.append((pic[0], pic[1], pic[2], pic[3], pic[4], pic[5]))
                
    


def getblocks():
    pass
