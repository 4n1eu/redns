

file = open("majVote.log", 'r').read().strip('\n').split('\n')
nsCount = 10

domains = dict()
deviationCount = [0]*(nsCount+1)
totalAnswerCount = 0
noAnswersCount = 0

nsNoResponse = [0]*(nsCount+1)
nsMinorityResponse = [0]*(nsCount+1)

for line in file:

    if "No answers" in line:
        noAnswersCount = noAnswersCount+1
        continue

    domain = line.split(" ")[2][1:-1]
    if domain not in domains.keys():
        domains[domain] = []

    if "final result is: " in line:
        final = line.split("final result is: ")[1][1:-1].split(", ")
        deviations = 0
        for answer in domains[domain]:
            if set(answer) != set(final):
                deviations = deviations+1
        deviationCount[deviations] = deviationCount[deviations]+1

    else:
        answer = line.split(" ready: ")[1][1:-1].split(", ")
        domains[domain].append(answer)
        totalAnswerCount = totalAnswerCount+1

# find how many ns answered
# find deviations from final answer
print("Number of responses with deviations from final answer: ", deviationCount)
print(f"total domains with answers: {len(domains)}")
print("should be equal to: ", deviationCount[0]+deviationCount[1]+deviationCount[2]+deviationCount[3]+deviationCount[4]+deviationCount[5]+deviationCount[6]+deviationCount[7]+deviationCount[8]+deviationCount[9]+deviationCount[10])
print(f"domains without any answer: {noAnswersCount}")
print(f"total number of domains logged: {len(domains)+noAnswersCount}")

# TODO: edit, if expectedAnswers changes
expectedAnswers = nsCount * len(domains)
print(f"\nNo or empty response: {expectedAnswers-totalAnswerCount}x ({(expectedAnswers-totalAnswerCount)/expectedAnswers*100}%)")