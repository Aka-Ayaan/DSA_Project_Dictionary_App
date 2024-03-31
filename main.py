def dictionary(filename):
    with open(filename) as f:
        data = f.readlines()
    for i in range(len(data)):
        data[i] = data[i].strip().split(',')
    dict = {}
    for i in range(len(data)):
        word = data[i].pop(0)
        if word in dict:
            dict[word].append(','.join(data[i]))
        else:
            dict[word] = [','.join(data[i])]
    print(dict)

dictionary('english.csv')