from . import bus

"""
Creates an array of Remote objects with Photos enabled and containing authentication method
"""
def listRemotes():
    rs = {}
    remotes = bus.getPhotoAccounts()
    for remote in remotes:
        pk = bus.getAccount(remote)
        ram = bus.getAuthMethod(pk)
        rs[remote] = ram

    return rs

def listRemoteDirs(rname):
    remote = f"providers.{rname.lower()}"
    # from .services import nextcloud as rem
    rem = __import__('providers.nextcloud')
    dirs = rem.listdirs()

def listRemotePics(remote, folder):
    pass

def getRemotePic(remote, path):
    pass

def putRemotePic(remote, path, content):
    pass
    
def scanRemote():
    remotes = listRemotes()
    for remote in remotes:
        rdirs = listRemoteDirs(remote)
