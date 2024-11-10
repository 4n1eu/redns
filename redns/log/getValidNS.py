file = open("log/majVote.log", "r")
text = file.read().rstrip('\n').split('\n')
validservers = []
for line in text:
    server = line.split(" ")[8]
    validservers.append(server)
    print(server)