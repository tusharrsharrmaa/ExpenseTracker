def Calculator(a , b , operation = "add"):
   operation = operation.strip().lower()
   if operation =="add":
      return a+b
   elif operation == "subtract":
      return a-b
   elif operation == "multiplication":
      return a*b
   elif operation == "division":
      return a/b
   else:
      return "Unknown operation"
   
print(Calculator(10,20,"Subtract"))
print(Calculator(20,300 , "Division "))
print(Calculator(200 , 400 ,"Multiplication"))
