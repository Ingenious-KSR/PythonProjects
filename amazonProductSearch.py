sw='armaze'
rw='xmazon'
i=0
count=0
ll=0
while i<len(rw):
    if rw[i] in sw[ll:]:
        ll=sw[ll:].index(rw[i])+1
        i+=1
    else:
        count+=1
        i+=1
print(count)
