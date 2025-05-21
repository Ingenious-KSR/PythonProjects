choice=0
while(choice==0):
    sal=int(input("Enter salary of the person"))
    if(sal>50000):
        tax=500
    else:
        tax=400
    print("tax to pay ",tax)
    print("Final in-hand",sal-tax)
    TempInp=int(input("Enter 0 for salary and tax calculation continuation otherwise enter 1 :"))
    choice=TempInp