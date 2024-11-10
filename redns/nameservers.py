def get(file, max=100000000000000000000000):
    try:
        file = open(file, 'r')
    except:
        file = open("ns/"+file, 'r')
    res = file.read().rstrip('\n').split('\n')[0:max]
    res = [i for i in res if '#' not in i]
    return res