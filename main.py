#CSV to dictionary word and meaning
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


#Conversion from dictionary to trie
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



#get function
def in_trie(trie, word):
    temp = word.upper()
    current_dict = trie
    for letter in temp:
        if letter not in current_dict:
            takeChoice = input("No such word in dictionary. Want to insert a new word?")
            if takeChoice.upper() == "YES":
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning)
                in_trie(trie,word)
            else:
                print("Exiting...")
        current_dict = current_dict[letter]
    if "_end" in current_dict:
        if current_dict["_end"][0][0] == ",":
            str1 = word + ": " + current_dict["_end"][0][1:]
        else:
            str1 = word + ": " + str(current_dict["_end"])
        print(str1)
        flag = False
        while not flag:
            choice = input("Is this the meaning you are lookin for?")
            if choice.upper() == "YES":
                return str1
            elif choice.upper() == "NO":
                print("Add your own meaning to this word:")
                meaning = input("Enter your meaning: ")
                trie = insert_trie(trie,word,meaning)
                str1 = word + ": " + str(current_dict["_end"])
                return str1
            else:
                print("Invalid Input: Enter \"yes\" or \"no\" to continue.")

    else:
        takeChoice = input("No such word in dictionary. Want to insert a new word?")
        if takeChoice.upper() == "YES":
            meaning = input("Enter your meaning: ")
            trie = insert_trie(trie,word,meaning)
            str1 = in_trie(trie,word)
            return str1
        else:
            print("Exiting...")
    





#Insert function
def insert_trie(trie,word,meaning):
    temp = word.upper()
    current_dict = trie
    flag = True
    for letter in temp:
        if letter not in current_dict:
            flag = False
            break
        current_dict = current_dict[letter]
    if flag:
        if "_end" in current_dict:
            if meaning in "_end":
                print("Word already exists")
            else:
                current_dict["_end"].append(meaning)
                print("Word entered succesfully")
                return trie
        else:
            current_dict["_end"] = [meaning]
            print("Word entered succesfully")
            return trie
    else:
        current_dict = trie
        for letter in temp:
            if letter not in current_dict:
                current_dict[letter] = {}
            current_dict = current_dict[letter]
        current_dict["_end"] = meaning
        print("yes")
        print("Word entered succesfully")
        return trie

dictionary = dictionary('english.csv')
trie = make_trie(dictionary)
userInput = int(input("Select your operation by entering the number:\n1)Insert\n2)Get\n"))
if userInput == 1:
    word = input("Enter your word")
    meaning = input("Enter your meaning: ")
    trie = insert_trie(trie,word,meaning)
    print(in_trie(trie,word))
elif userInput == 2:
    word = input("Enter your word")
    print(in_trie(trie,word))
