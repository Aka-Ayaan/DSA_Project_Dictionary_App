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
        word = word.upper()
        if word in dict:
            dict[word].append(','.join(data[i]))
        else:
            dict[word] = [','.join(data[i])]
    lst = list()
    for i in dict:
        if "-" == i[0] or "'" in i or "/" in i or "." in i or "1" in i or "(" in i or ")" in i:
            lst.append(i)
    for i in range(len(lst)):
        del dict[lst[i]]
    return dict

dictionary = dictionary('english.csv')

def wordDict(dictionary):
    returnDict = dict()
    upperletterHolder = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'," ","-"]
    for i in upperletterHolder:
        returnDict[i] = list()
    lst = list()
    for i in dictionary:
        lst.append(i)
    # print(lst)
    for i in range(len(lst)):
        print(lst[i])
        for j in range(1,len(lst[i])):
            if lst[i][j] not in returnDict[lst[i][j-1]]:
                returnDict[lst[i][j-1]].append(lst[i][j])
    return returnDict

print(wordDict(dictionary))