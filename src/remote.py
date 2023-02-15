import dbus

"""
Creates an array of Remote objects with Photos enabled and containing authentication method
"""
def listRemotes():
    remotes = dbus.getPhotoAccounts()
    for remote in remotes:
        pk = dbus.getAccount(remote)
        ram = dbus.getAuthMethod(pk)

    pass

def listRemoteDirs(remote):
    pass

def listRemotePics(remote, folder):
    pass

def getRemotePic(remote, path):
    pass

def putRemotePic(remote, path, content):
    pass
    
