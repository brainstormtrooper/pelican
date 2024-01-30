#cdata.py
import json
import os
import urllib
import hashlib
import sqlite3
import requests
from . import pager
from .locals import local
from .dbase import db
from .previews import preview
from webdav3.client import Client
from datetime import datetime
from pydbus import SessionBus
from pathlib import Path
from PIL import Image, ExifTags, TiffImagePlugin

cachepath = os.path.join(os.path.expanduser("~"), ".cache/pelican")

# con = sqlite3.connect(f"{cachepath}/pelican.db")

photospath = os.path.join(os.path.expanduser("~"), "Pictures/Photos")

datetimerange = [None, None]
proclock = False

def initdb():
    db3 = db(cachepath)
    if not db3.isInit():
        db3.initdb()

def getcacheloc(tn):
    previewpath = f"{cachepath}/previews"
    if not os.path.isdir(previewpath):
        os.makedirs(previewpath)
    fpath = f"{previewpath}/{tn}"
    return fpath

def setcache(tn, tocache):
    previewpath = f"{cachepath}/previews"
    if not os.path.isdir(previewpath):
        os.makedirs(previewpath)
    with open(f"{previewpath}/{tn}", "w+") as f:
        f.write(tocache)

def getcache(tn):
    with open(f"{cachepath}/previews/{tn}", "rb") as image:
        f = image.read()
        b = bytearray(f)
    return b

def addpreview():
    pass

def getlocation(lat, lon):
    locurl = f"https://nominatim.openstreetmap.org/reverse?format=geocodejson&lat={lat}&lon={lon}"
    rloc = requests.get(locurl)
    locob = json.loads(rloc.text)
    print(locob)
    town = locob['features'][0]['properties']['geocoding']['city']
    state = locob['features'][0]['properties']['geocoding']['state']
    country = locob['features'][0]['properties']['geocoding']['country']

    return town, state, country

def updatephrase(photo_id, words):
    db3 = db(cachepath)
    curphrase = db3.getphrase(photo_id)
    print(curphrase)
    curwords = curphrase.split(' ') if curphrase != '' else []
    newwords = list(set(curwords + words))
    newphrase = ' '.join(newwords)
    res = db3.updatephrase(photo_id, newphrase)

    return res


def updatecache():
    db3 = db(cachepath)
    onlyfiles = [f for f in os.listdir(photospath) if os.path.isfile(os.path.join(photospath, f))]
    print(onlyfiles)
    # saved = Query()
    for file in onlyfiles:
        # exists = db.search(saved.fileName == file)
        exists = db3.isphotoname(file)
        if not exists:
            print('new')
            newfile = local(photospath, file)
            
            # https://overpass-api.de/api/interpreter?data=[out:json];node[place~"^(village|town|city)$"](around:2500,44.05985555555556,5.130152777777778);out;
            # place~"^(village|town|city)$"
            # https://nominatim.openstreetmap.org/lookup?osm_ids=N26695231&format=json
            lat, lon, alt, direction = newfile.getCoordinates()
            
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
            img = newfile.getThumbnail()
            img.save(f"{cachepath}/previews/{newid}", 'jpeg')
            if lat and lon:
                town, state, country = getlocation(lat, lon)
                ct = db3.addlocationtophoto(newid, town, state, country)
                words = [town, state, country]
                updatephrase(newid, words)
    


def get100pics(pagelist, direction = 'down', datelimit = None, qty = 100):
    # https://stackoverflow.com/questions/64661336/return-value-in-a-python-thread
    db3 = db(cachepath)
    if None == datelimit:
        datelimit = datetime.utcnow().isoformat()
    picsrows = db3.getpicspage(direction, datelimit, qty)
    # t = getToken('Google')
    previewspath = f"{cachepath}/previews"
    for pic in picsrows:
        filename = pic[1]
        photospath = pic[2]
        print(photospath, filename)
        realpic = local(photospath, filename)
        if realpic.getExists():
            Preview = preview(pic[0], pic[1], pic[2], pic[3], cachepath)
            if Preview.exists:
                print('exists')
                pagelist.append(Preview)
    


def getblocks():
    pass
