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

# def wordDict(dictionary):
#     returnDict = dict()
#     upperletterHolder = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'," ","-"]
#     for i in upperletterHolder:
#         returnDict[i] = list()
#     lst = list()
#     for i in dictionary:
#         lst.append(i)
#     for i in range(len(lst)):
#         for j in range(1,len(lst[i])):
#             if lst[i][j] not in returnDict[lst[i][j-1]]:
#                 tempDict = dict()
#                 flag = False
#                 for z in dictionary:
#                     if z[:j+1] == lst[i][:j+1]:
#                         tempDict[z] = dictionary[z]
#                         flag = True
#                 returnDict[lst[i][j-1]].append((lst[i][j],flag,tempDict))
#                 # print(returnDict)
#     print(returnDict)

# wordDict(dictionary)

def make_trie(dictionary):
    words = []
    for i in dictionary:
        words.append(i)
    root = {}
    for word in words:
        current_dict = root
        for letter in word:
            if letter not in current_dict:
                current_dict[letter] = {}

            current_dict = current_dict[letter]
        current_dict["_end"] = dictionary[word]
    return root

trie = make_trie(dictionary)

def in_trie(trie, word):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            return "No such word in dictionary. Want to insert a new word?"
        current_dict = current_dict[letter]
    if "_end" in current_dict:
        if current_dict["_end"][0][0] == ",":
            str1 = word + ": " + current_dict["_end"][0][1:]
        else:
            str1 = word + ": " + current_dict["_end"][0]
        return str1
    else:
        return "No such word in dictionary. Want to insert a new word?"
    
print(in_trie(trie,"Aaronical"))



