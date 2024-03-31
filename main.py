def dictionary(filename):
    with open(filename) as f:
        data = f.readlines()
    for i in range(len(data)):
        if i >= 127357 and i <= 139844:
            data[i] = data[i].strip().split(' ')
        else:
            data[i] = data[i].strip().split(',')
    dict = {}
    for i in range(1,len(data)):
        word = data[i].pop(0)
        if word in dict:
            dict[word].append(','.join(data[i]))
        else:
            dict[word] = [','.join(data[i])]
    return dict

dictionary = dictionary('english.csv')
print(dictionary)

def wordDict(dictionary):
    returnDict = dict()
    upperletterHolder = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    specialCase = ["-","'"]
    for i in dictionary:
        if i in upperletterHolder:
            if i not in returnDict:
                returnDict[i] = list()
                returnDict[i.lower()] = list()
    for i in specialCase:
        returnDict[i] = list()
    print(returnDict)
    # for j in dictionary:
    #     if j not in upperletterHolder:
    #         print(j)
    #         returnDict[j[0]].append(j[1])
    # return returnDict

print(wordDict(dictionary))