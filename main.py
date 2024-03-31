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



