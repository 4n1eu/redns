def get(file, max=10):
    try:
        file = open(file, 'r')
    except:
        file = open("ns/"+file, 'r')
    res = file.read().rstrip('\n').split('\n')[0:max]
    file.close()
    return res