import bus

def connect():
    pass

def listDirs():
    pass

def listPics(fldr = None):
    ncfilesuri = bus.getBusData(nckey, 'Get', ['org.gnome.OnlineAccounts.Files', 'Uri'])
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
    pass

def download(path):
    pass

def upload(path, content):
    pass

def getPreviews(ncr):
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

    return tns
