income = [150000,25000]
expenses = [30000,15000]


# This function adds up an income list 
def calculate_total_income (income):
    return sum(income)
# This function adds up an expense list
def calculate_total_expenses (expenses):
    return sum(expenses)
# This function calculates the account balance by subtracting total expense from the total income
def calculate_balance(total_income, total_expenses):
    return total_income - total_expenses


total_income = calculate_total_income(income)

total_expenses = calculate_total_expenses(expenses)

calculate_balance = total_income - total_expenses

print (f"Total income: {total_income}")
print(f"Total expense: {total_expenses}")
print(f"Remaining balance: {calculate_balance}")

