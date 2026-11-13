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

def calculate_expenses_by_category(expenses):
    category_totals = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]
        
        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += amount

    return category_totals

def view_all_expenses():
    print("\n========== ALL EXPENSES ==========")

    for expense in expenses:
        print(f"Description: {expense['description']}")
        print(f"Amount: {format_currency(expense['amount'])}")
        print(f"Category: {expense['category']}")
        print("--------------------------")

def add_expense():
    
    while True:  
        expense_description = input("What did you buy? ")

        while True:
            amount_in_pence = input("Enter amount in pence: ")

            if amount_in_pence.isdigit():
                amount_in_pence = int(amount_in_pence)
                break
            else:
                print("Please enter a valid number")
            
        enter_category = input("Enter category: ")
        expense = {'description': expense_description, 'amount': amount_in_pence, 'category': enter_category}
        expenses.append(expense)
    
        while True:
            add_another = input("Add another expense? (yes/no): ").lower()
            if add_another == "yes" or add_another == "no":
                break
            else:
                print("Please enter yes or no")
        if add_another == "no":
            break
        
def view_expenses_by_category():
    category_totals = calculate_expenses_by_category(expenses)
    print("\n========== SPENDING BY CATEGORY ==========")
        
    for category, amount in category_totals.items():
        print(f"{category}: {format_currency(amount)}")

def view_financial_summary():
    
    total_income = calculate_total_income(income)

    total_expenses = calculate_total_expenses(expenses)

    balance = calculate_balance(total_income, total_expenses)
    
    print("\n========== FINANCIAL SUMMARY ==========")

    print(f"Total income: {format_currency(total_income)}")
    print(f"Total expenses: {format_currency(total_expenses)}")
    print(f"Remaining balance: {format_currency(balance)}")


while True:
    print("========== PENNYWISE ==========")

    # Menu options
    print("1. Add an expense")
    print("2. View all expenses")
    print("3. View spending by category")
    print("4. View financial summary")
    print("5 .Exit")
    
    choice = input("Please select an option: ")
    
    if choice == "1":
        add_expense()
    elif choice == "2":
        view_all_expenses()
    elif choice == "3":
        view_expenses_by_category()
    elif choice == "4":
        view_financial_summary()
    elif choice == "5":
        break
    
    else:
        print("Invalid option. Please select a number between 1 and 5.")

