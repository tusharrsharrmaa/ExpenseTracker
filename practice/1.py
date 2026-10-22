##Ask the user for an expense amount. If it is under 100, print “Small expense”. If it is 100 to 999, print “Medium expense”. Otherwise, print “Big expense”. Test it with 99, 100, 999 and 1000.

user = int(input("Enter Expense amount "))
if user < 100:
   print("Small expense")
elif user < 1000:
   print("Medium number")
else:
   print("Big number")