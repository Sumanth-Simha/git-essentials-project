import json
import os

from flask import Flask, jsonify, render_template, request

EXPENSES_FILE = "expenses.json"
app = Flask(__name__)


def load_expenses():
    if not os.path.exists(EXPENSES_FILE):
        return []
    try:
        with open(EXPENSES_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


def add_expense(expense):
    new_expense = input("enter expense: ")
    expense.append(new_expense)
    save_expenses(expense)
    print(f"expense {new_expense} added successfully")


def view_expense(expense):
    if not expense:
        print("no expenses to view")
        return
    print("expenses:")
    for idx, item in enumerate(expense, start=1):
        print(f"{idx}. {item}")
    split_expense(expense)
def split_expense(expense):
    if not expense:
        print("no expenses to split")
        return
    total_expense = sum(float(item) for item in expense)
    num_people = int(input("enter number of people to split the expense: "))
    if num_people <= 0:
        print("number of people must be greater than zero")
        return
    split_amount = total_expense / num_people
    print(f"total expense: {total_expense}")
    print(f"each person should pay: {split_amount}")        

def main():
    expense = load_expenses()
    while True:
        print("\n1. Add expense")
        print("2. View expense")
        print("3. Exit")
        choice = input("enter your choice: ")
        if choice == "1":
            add_expense(expense)
        elif choice == "2":
            view_expense(expense)
        elif choice == "3":
            print("exiting the program")
            break
        else:
            print("invalid choice")


@app.get("/")
def index():
    expenses = load_expenses()
    total = sum(float(item) for item in expenses)
    return render_template("index.html", expenses=expenses, total=total)


@app.post("/expenses")
def create_expense():
    payload = request.get_json(silent=True) or {}
    value = payload.get("expense")
    if value is None or not str(value).strip():
        return jsonify(error="expense is required"), 400
    try:
        float(value)
    except (TypeError, ValueError):
        return jsonify(error="expense must be a number"), 400

    expenses = load_expenses()
    expenses.append(str(value).strip())
    save_expenses(expenses)
    return jsonify(expense=expenses[-1], expenses=expenses), 201


@app.get("/expenses/split")
def split_expenses():
    expenses = load_expenses()
    try:
        people = int(request.args.get("people", ""))
    except ValueError:
        return jsonify(error="people must be a whole number"), 400
    if people <= 0:
        return jsonify(error="people must be greater than zero"), 400

    total = sum(float(item) for item in expenses)
    return jsonify(total=total, people=people, per_person=total / people)


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
