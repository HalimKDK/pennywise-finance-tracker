from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import initialize_database
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("Set SECRET_KEY before starting PennyWise.")
initialize_database()

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("pennywise.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    cursor.execute("""
    SELECT SUM(amount)
    FROM transactions
    WHERE user_id = ?
    AND transaction_type = 'income'
    """, (session["user_id"],))

    total_income = cursor.fetchone()[0]
    
    cursor.execute("""
    SELECT SUM(amount)
    FROM transactions
    WHERE user_id = ?
    AND transaction_type = 'expense'
    """, (session["user_id"],))

    total_expenses = cursor.fetchone()[0]
    total_income = total_income or 0
    total_expenses = total_expenses or 0
    total_balance = total_income - total_expenses
    

    try:
        cursor.execute(
            """
            SELECT description, category, amount, transaction_type, transaction_date
            FROM transactions
            WHERE user_id = ?
            ORDER BY transaction_date DESC, id DESC
            LIMIT 5
            """,
            (session["user_id"],),
        )
        recent_transactions = cursor.fetchall()

        cursor.execute(
            "SELECT username FROM users WHERE id = ?",
            (session["user_id"],),
        )
        user = cursor.fetchone()
        
        cursor.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE user_id = ? AND transaction_type = 'expense'
        GROUP BY category
        ORDER BY total DESC
        """,
        (session["user_id"],),
        )
        expense_breakdown = cursor.fetchall()
        
        today = date.today()
        current_month = today.strftime("%Y-%m")
        month_label = today.strftime("%B %Y")

        cursor.execute(
        """
        SELECT
        COALESCE(SUM(CASE
            WHEN transaction_type = 'income' THEN amount
            ELSE 0
        END), 0) AS income,
        COALESCE(SUM(CASE
            WHEN transaction_type = 'expense' THEN amount
            ELSE 0
        END), 0) AS expenses
        FROM transactions
        WHERE user_id = ?
        AND substr(transaction_date, 1, 7) = ?
        """,
        (session["user_id"], current_month),
        )
        month_totals = cursor.fetchone()

        month_income = month_totals["income"]
        month_expenses = month_totals["expenses"]
        month_balance = month_income - month_expenses

    finally:
        connection.close()

    return render_template(
    "index.html",
    username=user["username"],
    total_balance=total_balance,
    total_income=total_income,
    total_expenses=total_expenses,
    recent_transactions=recent_transactions,
    expense_breakdown=expense_breakdown,
    month_label=month_label,
    month_income=month_income,
    month_expenses=month_expenses,
    month_balance=month_balance,
)

@app.route("/transactions/add", methods=["GET", "POST"])
def add_transaction():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        transaction_type = request.form.get("transaction_type", "")
        transaction_date = request.form.get("transaction_date", "")

        if not description or not category:
            flash("Enter a description and category.")
            return redirect(url_for("add_transaction"))

        if transaction_type not in ("income", "expense"):
            flash("Choose income or expense.")
            return redirect(url_for("add_transaction"))

        try:
            date.fromisoformat(transaction_date)
            amount_pounds = Decimal(request.form.get("amount", ""))

            if (
                amount_pounds <= 0
                or amount_pounds != amount_pounds.quantize(Decimal("0.01"))
            ):
                raise InvalidOperation

            amount_pence = int(amount_pounds * 100)

        except (ValueError, InvalidOperation):
            flash("Enter a valid date and an amount with up to two decimal places.")
            return redirect(url_for("add_transaction"))

        connection = sqlite3.connect("pennywise.db")

        try:
            connection.execute(
                """
                INSERT INTO transactions
                    (user_id, description, amount, category,
                     transaction_type, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    description,
                    amount_pence,
                    category,
                    transaction_type,
                    transaction_date,
                ),
            )
            connection.commit()
        finally:
            connection.close()

        flash("Transaction saved.")
        return redirect(url_for("home"))

    return render_template("add_transaction.html")
    
@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("pennywise.db")
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()
        filter_type = request.args.get("type", "all")

        if filter_type not in ("all", "income", "expense"):
            filter_type = "all"

        if filter_type == "all":
            cursor.execute(
                """
                SELECT id, description, amount, category,
                       transaction_type, transaction_date
                FROM transactions
                WHERE user_id = ?
                ORDER BY transaction_date DESC, id DESC
                """,
                (session["user_id"],),
            )
        else:
            cursor.execute(
                """
                SELECT id, description, amount, category,
                       transaction_type, transaction_date
                FROM transactions
                WHERE user_id = ? AND transaction_type = ?
                ORDER BY transaction_date DESC, id DESC
                """,
                (session["user_id"], filter_type),
            )

        transactions = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "transactions.html",
        transactions=transactions,
        filter_type=filter_type,
    )

@app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("pennywise.db")
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, description, amount, category,
                   transaction_type, transaction_date
            FROM transactions
            WHERE id = ? AND user_id = ?
            """,
            (transaction_id, session["user_id"]),
        )
        transaction = cursor.fetchone()

        if transaction is None:
            return redirect(url_for("transactions"))

        if request.method == "POST":
            description = request.form.get("description", "").strip()
            category = request.form.get("category", "").strip()
            transaction_type = request.form.get("transaction_type", "")
            transaction_date = request.form.get("transaction_date", "")

            if not description or not category:
                return render_template(
                    "edit_transaction.html",
                    transaction=transaction,
                    error="Enter a description and category.",
                )

            if transaction_type not in ("income", "expense"):
                return render_template(
                    "edit_transaction.html",
                    transaction=transaction,
                    error="Choose income or expense.",
                )

            try:
                date.fromisoformat(transaction_date)
                amount_pounds = Decimal(request.form.get("amount", ""))

                if (
                    not amount_pounds.is_finite()
                    or amount_pounds <= 0
                    or amount_pounds != amount_pounds.quantize(Decimal("0.01"))
                ):
                    raise InvalidOperation

                amount_pence = int(amount_pounds * 100)

            except (ValueError, InvalidOperation):
                return render_template(
                    "edit_transaction.html",
                    transaction=transaction,
                    error="Enter a valid date and an amount with up to two decimal places.",
                )

            cursor.execute(
                """
                UPDATE transactions
                SET description = ?, amount = ?, category = ?,
                    transaction_type = ?, transaction_date = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    description,
                    amount_pence,
                    category,
                    transaction_type,
                    transaction_date,
                    transaction_id,
                    session["user_id"],
                ),
            )
            connection.commit()
            return redirect(url_for("transactions"))

    finally:
        connection.close()

    return render_template(
        "edit_transaction.html",
        transaction=transaction,
    )
    
@app.route(
    "/transactions/<int:transaction_id>/delete",
    methods=["POST"],
)
def delete_transaction(transaction_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("pennywise.db")

    try:
        connection.execute(
            """
            DELETE FROM transactions
            WHERE id = ? AND user_id = ?
            """,
            (transaction_id, session["user_id"]),
        )
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for("transactions"))
    
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = sqlite3.connect("pennywise.db")
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))

            connection.commit()

            flash("Account created successfully!")

            return redirect(url_for("register"))

        except sqlite3.IntegrityError:

            flash("This email address is already registered.")

        finally:
            connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = sqlite3.connect("pennywise.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):

                session["user_id"] = user["id"]

                flash("Login successful!")

                return redirect(url_for("home"))

            else:
                flash("Incorrect email or password.")

        finally:
            connection.close()

    return render_template("login.html")

@app.route("/settings")
def settings():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("pennywise.db")
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT username, email FROM users WHERE id = ?",
            (session["user_id"],),
        )
        user = cursor.fetchone()
    finally:
        connection.close()

    return render_template("settings.html", user=user)




if __name__ == "__main__":
    app.run(debug=True)