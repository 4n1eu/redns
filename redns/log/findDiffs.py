import math

file = open("majVote.log", 'r').read().strip('\n').split('\n')
nsCount = 10

results = dict()
deviationCount = [0]*(nsCount+1)
totalAnswerCount = 0
noAnswersCount = 0
nsResponses = [0]*nsCount

nsMinorityResponse = [0]*(nsCount+1)

for i, line in enumerate(file):
    if (i%100000 ==0): print(f"{math.floor(i/len(file)*100)}%", end='\r')

    if "No answers" in line:
        noAnswersCount = noAnswersCount+1
        continue

    domain = line.split(" ")[2][1:-1]
    if domain not in results.keys():
        results[domain] = []

    if "final result is: " in line:
        final = line.split("final result is: ")[1][1:-1].split(", ")
        deviations = 0
        for answer in results[domain]:
            if set(answer) != set(final):
                deviations = deviations+1
        deviationCount[deviations] = deviationCount[deviations]+1

    else:
        answer = line.split(" ready: ")[1][1:-1].split(", ")
        results[domain].append(answer)
        totalAnswerCount = totalAnswerCount+1
    
        ns = int(line.split(" ")[6].split("/")[0])-1
        nsResponses[ns] = nsResponses[ns]+1

# find how many ns answered
# find deviations from final answer
print("Number of responses with deviations from final answer: ", deviationCount)
print(f"total domains with answers: {len(results)}")
print(f"domains without any answer: {noAnswersCount}")
print(f"total number of domains logged: {len(results)+noAnswersCount}")

# TODO: edit, if expectedAnswers changes
expectedAnswers = nsCount * len(results)
print(f"\nNo or empty response: {expectedAnswers-totalAnswerCount}x ({(expectedAnswers-totalAnswerCount)/expectedAnswers*100}%)")
for i in range(nsCount):
    nsResponses[i] = len(results) - nsResponses[i]
print(f"anzahl fehlender antworten - by ns: {nsResponses}")