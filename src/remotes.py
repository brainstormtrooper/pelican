import bus

"""
Creates an array of Remote objects with Photos enabled and containing authentication method
"""
def listRemotes():
    remotes = bus.getPhotoAccounts()
    for remote in remotes:
        pk = bus.getAccount(remote)
        ram = bus.getAuthMethod(pk)

    pass

def listRemoteDirs(remote):
    pass

def listRemotePics(remote, folder):
    pass

def getRemotePic(remote, path):
    pass

def putRemotePic(remote, path, content):
    pass
    
def scanRemote():
    remotes = listRemotes()
