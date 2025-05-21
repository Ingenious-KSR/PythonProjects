n=int(input())
s=1
e=n*2-1
for i in range(1,n+1):
    for j in range(1,n*2):
        if j==s or j==e:
            print(i,end=" ")
        elif j<e:
            print(" ",end=" ")
        else:
            break
    print()
    s+=1
    e-=1
st=n-1
en=n+1
for k in range(n-1,0,-1):
    for l in range(1,n*2):
        if l==st or l==en:
            print(k,end=" ")
        elif l<en:
            print(" ",end=" ")
        else:
            break
    print()
    st-=1
    en+=1
