#cdata.py
import json
import os
import urllib
import hashlib
import sqlite3
import requests
from .locals import local
from .dbase import db
from webdav3.client import Client
from datetime import datetime
from pydbus import SessionBus
from pathlib import Path
from PIL import Image, ExifTags, TiffImagePlugin

cachepath = os.path.join(os.path.expanduser("~"), ".cache/pelican")

# con = sqlite3.connect(f"{cachepath}/pelican.db")
db3 = db(cachepath)
photospath = os.path.join(os.path.expanduser("~"), "Pictures/Photos")

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

def safeType(v):
    try:
        v = v.decode()
    except (UnicodeDecodeError, AttributeError):
        if type(v) is TiffImagePlugin.IFDRational:
            v = int(v)
    if type(v) is tuple:
        v = [float(i) for i in v]
    return v


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
    curphrase = db3.getphrase(photo_id)
    print(curphrase)
    curwords = curphrase.split(' ') if curphrase != '' else []
    newwords = list(set(curwords + words))
    newphrase = ' '.join(newwords)
    res = db3.updatephrase(photo_id, newphrase)

    return res


def updatecache():
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
                os.path.join(photospath, file), 
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
            
            town, state, country = getlocation(lat, lon)
            ct = db3.addlocationtophoto(newid, town, state, country)
            words = [town, state, country]
            updatephrase(newid, words)
            exit()

def get100pics():
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')
    picsrows = db3.getpicspage('down', now, 100)
    # t = getToken('Google')
    previewpath = f"{cachepath}/previews"
    tns = []
    with os.scandir(previewpath) as entries:
        for entry in entries:
            tns.append(entry.name)
            print(entry.name)

    """
    testphotopath = ncr[1]['path']
    dlres = client.download_sync(remote_path='/Photos/Birdie.jpg', local_path='/home/rick/Downloads/birdietest.jpg')
    print(dlres)

    thumbprop = client.get_property(f"{photosEndpoint}/Birdie.jpg", { 'namespace': 'http://nextcloud.org/ns', 'name': 'has-preview'})
    print(thumbprop)

    testthumb = f"preview.png?file={urllib.parse.quote('/Photos/Birdie.jpg')}&x=250&y=250http&a=1&mode=cover&forceIcon=0"
    testthumburibase = 'https://cloud2.rickopper.com/index.php/core/'
    options = {
         'webdav_hostname': testthumburibase,
         'webdav_login':    usr,
         'webdav_password': pw,
         'webdav_timeout': 60,
         'webdav_override_methods': {
            'info': 'HEAD'
        }
    }
    thumbclient = Client(options)

    # testres = requests.get(testthumb, stream=True).text
    testres = thumbclient.download_sync(remote_path=testthumb, local_path='~/Downloads/birdiethumb.jpg')

    print(testres)
    """
    return tns
