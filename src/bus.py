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

    # print(remote_object.Introspect())
    res = remote_object.__getattribute__(returnable)(*args, **kwargs)
    return res

def getAuthMethod(pk):
    # org.gnome.OnlineAccounts.PasswordBased
    # org.gnome.OnlineAccounts.OAuth2Based
    res = {}
    try:
        res['token'] = getBusData(pk, 'GetAccessToken')
    except AttributeError:
        Id = getBusData(pk, 'Get', ['org.gnome.OnlineAccounts.Account', 'Id'])
        res['user'] = getBusData(pk, 'Get', ['org.gnome.OnlineAccounts.Account', 'Identity'])
        res['password'] = getBusData(pk, 'GetPassword', [Id])
    # print(res)
    return res

def getPhotoAccounts():
    res = {}
    # return ['Google', 'Nextcloud']
    # org.gnome.OnlineAccounts.Photos
    accts = getBusData("/org/gnome/OnlineAccounts", "GetManagedObjects")
    print(accts)
    for k in accts:
        try:
            puri = getBusData(k, 'Get', ['org.gnome.OnlineAccounts.Photos', 'Uri'])
            provider = accts[k]['org.gnome.OnlineAccounts.Account']['ProviderName']
            res[provider] = puri
        except Exception:
            try:
                puri = getBusData(k, 'Get', ['org.gnome.OnlineAccounts.Files', 'Uri'])
                provider = accts[k]['org.gnome.OnlineAccounts.Account']['ProviderName']
                res[provider] = puri
            except Exception:
                pass
    return res

def getAccount(provider):
    res = None
    authdata = None
    accts = getBusData("/org/gnome/OnlineAccounts", "GetManagedObjects")
    # print(accts)
    for k in accts:
        # print('>>>  ACCT INFO   >>>')
        # print(accts[k])
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


