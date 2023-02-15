#cdata.py
import json
import os
import requests
import urllib
import dbus
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


def get100pics():

    t = getToken('Google')
    nckey = getAccount('Nextcloud')
    usr, pw = getCreds('Nextcloud')

    ncfilesuri = getBusData(nckey, 'Get', ['org.gnome.OnlineAccounts.Files', 'Uri'])
    photosEndpoint = '/Photos'
    print(ncfilesuri)

    options = {
         'webdav_hostname': ncfilesuri.replace('davs://', 'https://'),
         'webdav_login':    usr,
         'webdav_password': pw,
         'webdav_timeout': 60
    }
    client = Client(options)
    # client.verify = False
    # ncr = client.execute_request("list", 'directory_name')
    ncr = client.list(photosEndpoint, get_info=True)
    print(ncr)
    tns = []
    for rec in ncr:
        if rec['isdir'] == False and 'image' in rec['content_type']:
            # rectn = rec['etag'] if 'etag' in rec.keys() else urllib.parse.quote(rec['path'])
            p = Path(rec['path'])
            namepath = p.relative_to(f"/remote.php/webdav{photosEndpoint}")
            print(namepath)
            tns.append(namepath)
            remotepath = f"{photosEndpoint}/{namepath}"
            testpath = getcacheloc(namepath)
            if not os.path.isfile(testpath):
                client.download_sync(remote_path=remotepath, local_path=testpath)

    with os.scandir(photospath) as entries:
        for entry in entries:
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


    with open('/home/rick/Downloads/birdietest.jpg', "rb") as image:
        f = image.read()
        b = bytearray(f)

    endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=100"
    auth = f"Bearer {t}"
    # print(auth)
    myheaders = {
        'Authorization': auth,
        'Content-type': 'application/json'
    }
    body = { 'pageSize': '100' }

    r = requests.request(method='get', url=endpoint, headers=myheaders)

    print(r.text)

    return tns
