file = open("../log/majVote.log", "r")
text = file.read().rstrip('\n').split('\n')
validservers = []
for line in text:
    if "final result" in line or "No answers" in line:
        continue
    server = line.split(" ")[8]
    validservers.append(server)
    print(server)