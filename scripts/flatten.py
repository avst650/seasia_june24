a = [[1, 2], [[[[3, 4, 5], 6]]], '7', [8, [9, [10, 11], 12, [13, 14, [15, [[16, 17], 18]]]]]]
l=[]

def ls(x):
    for j in x:
        if isinstance(j, list):
            ls(j)
        else:
            l.append(j)    

ls(a)
print(l)
