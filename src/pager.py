queue = []

def pushelement(element):
    queue.append(element)
    sortqueue()

def sortqueue(): 
    # sort(key=lambda x: x.count, reverse=True) <- descending order
    queue.sort(key=lambda x: x.timestamp)

def popelement():
    pass