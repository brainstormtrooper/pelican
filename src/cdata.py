#cdata.py
import json
import os
import requests
import urllib
from . import locals
from . import remotes
from tinydb import TinyDB, Query
from webdav3.client import Client
from pydbus import SessionBus
from pathlib import Path

cachepath = os.path.join(os.path.expanduser("~"), ".cache/pelican")
dbfile = f"{cachepath}/db.json"
photospath = os.path.join(os.path.expanduser("~"), "Pictures")

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

def updatecache():
    locals.scanLocal()
    remotes.scanRemote()

def get100pics():

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
