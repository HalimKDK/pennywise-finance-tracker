income = [150000,25000]

expenses = [
    {
    "description": "Train ticket",
    "amount": 1500,
    "category": "Transport"
    },

     {
        "description": "Lunch",
        "amount": 800,
        "category": "Food"
    }

]


# This function adds up an income list 
def calculate_total_income (income):
    return sum(income)
# This function calculates the account balance by subtracting total expense from the total income
def calculate_balance(total_income, total_expenses):
    return total_income - total_expenses
# This function adds up an expense list
def calculate_total_expenses(expenses):
    total_expenses = 0

    for expense in expenses:   
        total_expenses += expense["amount"]
    return total_expenses

def format_currency(amount):
    amount /= 100
    
    return f"£{amount:.2f}"
    
    


total_income = calculate_total_income(income)

total_expenses = calculate_total_expenses(expenses)

balance = calculate_balance(total_income, total_expenses)

print(f"Total income: {format_currency(total_income)}")
print(f"Total expenses: {format_currency(total_expenses)}")
print(f"Remaining balance: {format_currency(balance)}")


#print(expenses[0])
# print(expenses["amount"])
# print(expenses["category"])