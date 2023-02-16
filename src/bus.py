#dbus.py

from pydbus import SessionBus

def getBusData(obpath, returnable, args = [], kwargs = {}):
    res = None
    bus = SessionBus()

    #org.freedesktop.DBus
    #org.gnome.OnlineAccounts
    remote_object = bus.get(
        "org.gnome.OnlineAccounts", # Bus name
        obpath # Object path
    )

    print(remote_object.Introspect())
    res = remote_object.__getattribute__(returnable)(*args, **kwargs)
    return res

def getAuthMethod(pk):
    pinfo = getBusData(pk, "Introspect")
    pass

def getPhotoAccounts():
    return ['google', 'nextcloud']

def getAccount(provider):
    res = None
    authdata = None
    accts = getBusData("/org/gnome/OnlineAccounts", "GetManagedObjects")
    for k in accts:
        if ('org.gnome.OnlineAccounts.Account' in accts[k].keys() and accts[k]['org.gnome.OnlineAccounts.Account']['ProviderName'] == provider):
            res = k
    return res


def getCreds(provider):
    pk = getAccount(provider)
    pinfo = getBusData(pk, "Introspect")
    Id = getBusData(pk, 'Get', ['org.gnome.OnlineAccounts.Account', 'Id'])
    usr = getBusData(pk, 'Get', ['org.gnome.OnlineAccounts.Account', 'Identity'])
    pw = getBusData(pk, 'GetPassword', [Id])

    return usr, pw

def getToken(provider):
    acct = getAccount(provider)
    accto = getBusData(acct, 'GetAccessToken')
    # print(accto)


    # print(session.get('https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=100').json())
    return accto[0]


