import sqlite3 as sq
import tkinter as tk
from tkinter import messagebox

class DataBaseTasks:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sq.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS bank
                            (account_id TEXT NOT NULL PRIMARY KEY,
                             password TEXT NOT NULL,
                             email TEXT NOT NULL,
                             phone TEXT NOT NULL,
                             address TEXT NOT NULL,
                             balance INTEGER NOT NULL);''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS transaction_history
                            (account_id TEXT NOT NULL,
                             transaction_type VARCHAR(50) NOT NULL,
                             amount DECIMAL(10, 2) NOT NULL,
                             transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             description VARCHAR(255),
                             FOREIGN KEY (account_id) REFERENCES bank(account_id));''')
        self.cur.execute('''CREATE TABLE IF NOT EXIST admin
        (username VARCHAR(15),
        password VARCHAR(12));''')
        self.conn.commit()

    def create_account(self, account_id, password, email, phone, address, balance):
        try:
            self.cur.execute('INSERT INTO bank VALUES (?, ?, ?, ?, ?, ?)', (account_id, password, email, phone, address, balance))
            self.conn.commit()
        except sq.OperationalError:
            messagebox.showerror("Error", "Account ID already exists")

    def view_account(self, password):
        try:
            self.cur.execute('SELECT * FROM bank WHERE password=?', (password,))
            data = self.cur.fetchall()
            return data
        except sq.OperationalError:
            messagebox.showerror("Error", "Invalid password")
    def delete_account(self, password):
        try:
            self.cur.execute('DELETE FROM bank WHERE password=?', (password,))
            self.conn.commit()
        except sq.OperationalError:
            messagebox.showerror("Error", "Invalid password")

    def update_account(self, account_id, password, email, phone, address, balance):
        try:
            self.cur.execute('UPDATE bank SET account_id=?, password=?, email=?, phone=?, address=? WHERE password=?', (account_id, password, email, phone, address, password))
            self.conn.commit()
        except sq.OperationalError:
            messagebox.showerror("Error", "Invalid password")
    def deposit_amount(self, amount, account_id, password):
        try:
            self.cur.execute('SELECT balance FROM bank WHERE password=?', (password,))
            balance = self.cur.fetchone()[0]
            new_balance = balance + amount
            self.cur.execute('UPDATE bank SET balance=? WHERE password=?', (new_balance, password))
            self.conn.commit()
            self.record_transaction_detail(account_id, "deposit", amount, f"{account_id} deposit amount {amount} successfully")
        except sq.OperationalError:
            messagebox.showerror("Error", "Invalid password")

    def withdraw_amount(self, account_id, password, amount):
        self.cur.execute('SELECT balance FROM bank WHERE password=?', (password,))
        balance = self.cur.fetchone()[0]
        new_balance = balance - amount
        self.cur.execute('UPDATE bank SET balance=? WHERE password=?', (new_balance, password))
        self.conn.commit()
        self.record_transaction_detail(account_id, "withdrawal", amount, f"{account_id} withdraw amount {amount} successfully")

    def transfer_amount(self, sender_account_id, receiver_account_id, amount):
        self.cur.execute('SELECT balance FROM bank WHERE account_id=?', (sender_account_id,))
        sender_balance = self.cur.fetchone()[0]
        new_sender_balance = sender_balance - amount
        self.cur.execute('UPDATE bank SET balance=? WHERE account_id=?', (new_sender_balance, sender_account_id))
        self.cur.execute('SELECT balance FROM bank WHERE account_id=?', (receiver_account_id,))
        receiver_balance = self.cur.fetchone()[0]
        new_receiver_balance = receiver_balance + amount
        self.cur.execute('UPDATE bank SET balance=? WHERE account_id=?', (new_receiver_balance, receiver_account_id))
        self.conn.commit()
        self.record_transaction_detail(sender_account_id, "transfer", amount, f"{sender_account_id} transfer amount {amount} to {receiver_account_id} successfully")

    def view_balance(self, account_id):
        try:
            self.cur.execute('SELECT balance FROM bank WHERE account_id=?', (account_id,))
            balance = self.cur.fetchone()[0]
            return balance
        except sq.OperationalError:
            messagebox.showerror("Error", "Invalid account ID")

    def record_transaction_detail(self, account_id, transaction_type, transaction_amount, description):
        try:
            self.cur.execute('INSERT INTO transaction_history (account_id, transaction_type, amount, transaction_date, description) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)', (account_id, transaction_type, transaction_amount, description))
            self.conn.commit()
        except sq.OperationalError:
            messagebox.showerror("Error , Invalid account id")
    def transaction_history(self, account_id):
        try:
            self.cur.execute('SELECT * FROM transaction_history WHERE account_id=?', (account_id,))
            data = self.cur.fetchall()
            return data
        except sq.OperationalError:
            messagebox.showerror("Error ,Invalid  Account Id")
    def get_password(account_id):
        self.cur.execute('SELECT password FROM bank WHERE account_id=?', (account_id,))
        password = self.cur.fetchone()[0]
        return password 
    def get_account_id(password):
        self.cur.execute('SELECT account_id FROM bank WHERE password=?', (password,))
        account_id = self.cur.fetchone()[0]
        return account_id
self.conn.close()

class Bank:
    def __init__(self):
        self.db = DataBaseTasks('bank.db')
    def authentication(self,account_id , password):
        stored_id=self.db.get_account_id(password)
        stored_password=self.db.get_password(account_id)
    if (stored_password is not None and stored_password == password) and (stored_id is not None and stored_id== account_id):
        return True
    else:
        return False
    def create_account(self, account_id, password, email, phone, address, balance):
        self.db.create_account(account_id, password, email, phone, address, balance)
    def view_account(self,account_id,password):
        if self.authentication(account_id,password)==True:
            self.db.view_account(account_id)
        else:
            messagebox.showerror("Error","Invalid Account Id or Password")
    def delete_account(self, password):
        pass

    def update_account(self, account_id, password, email, phone, address, balance):
        if self.authentication(account_id,password)==True:
            self.db.update_account( account_id, password, email, phone, address, balance)
        else:
            messagebox.showerror("Error","Invalid Account Id or Password")
    def deposit_amount(self, amount, account_id, password):
        if self.authentication(account_id,password)==True:
            self.db.deposit_amount(amount,account_id,password)
        else:
            messagebox.showerror("Error","Invalid Account Id or Password")
    def withdraw_amount(self, account_id, password, amount):
        pass
    def transfer_amount(self, sender_account_id, receiver_account_id, amount):
        pass

    def view_balance(self, account_id):
        pass
    def record_transaction_detail(self, account_id, transaction_type, transaction_amount, description):
        pass
    def transaction_history(self, account_id):    
        pass

class App:
    def __init__(self, master):
        self.master = master
        self.bank = Bank()
        self.create_widgets()

    def create_widgets(self):
        self.account_id_label = tk.Label(self.master, text="Account ID:")
        self.account_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.account_id_entry = tk.Entry(self.master)
        self.account_id_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.master, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.email_label = tk.Label(self.master, text="Email:")
        self.email_label.grid(row=2, column=0, padx=5, pady=5)
        self.email_entry = tk.Entry(self.master)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)

        self.phone_label = tk.Label(self.master, text="Phone:")
        self.phone_label=grid(row=2, column=2, padx=5, pady=5)
        self.phone_entry = tk.Entry(self.master)
        self.phone_entry.grid(row=2, column=3, padx=5, pady=5)

        self.address_label = tk.Label(self.master, text="Address:")
        self.address_label.grid(row=3, column=0, padx=5, pady=5)
        self.address_entry = tk.Entry(self.master)
        self.address_entry.grid(row=3, column=1, padx=5, pady=5)

        self.balance_label = tk.Label(self.master, text="Balance:")
        self.balance_label.grid(row=4, column=0, padx=5, pady=5)
        self.balance_entry = tk.Entry(self.master)
        self.balance_entry.grid(row=4, column=1, padx=5, pady=5)

        self.create_account_button = tk.Button(self.master, text="Create Account", command=self.create_account)
        self.create_account_button.grid(row=5, column=0, padx=5, pady=5)

        self.view_account_button = tk.Button(self.master, text="View Account", command=self.view_account)
        self.view_account_button.grid(row=5, column=1, padx=5, pady=5)

        self.delete_account_button = tk.Button(self.master,text="Delete Account", command=self.delete_account)
        self.delete_account_button.grid(row=5, column=2, padx=5, pady=5)

        self.withdraw_button = tk.Button(self.master, text="Withdraw", command=self.withdraw)
        self.withdraw_button.grid(row=6, column=0, padx=5, pady=5)

        self.deposit_button = tk.Button(self.master, text="Deposit", command=self.deposit)
        self.deposit_button.grid(row=6, column=1, padx=5, pady=5)

        self.transfer_button = tk.Button(self.master, text="Transfer", command=self.transfer)
        self.transfer_button.grid(row=6, column=2, padx=5, pady=5)


    def create_account(self):
        account_id = self.account_id_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()
        balance = self.balance_entry.get()
        self.bank.create_account(account_id, password, email, phone, address, balance)

    def view_account(self):
        password = self.password_entry.get()
        data = self.bank.view_account(password)
        messagebox.showinfo("Account Details", f"Account ID: {data[0][0]}\nPassword: {data[0][1]}\nEmail: {data[0][2]}\nPhone: {data[0][3]}\nAddress: {data[0][4]}\nBalance: {data[0][5]}")
    def delete_account(self):
        password = self.password_entry.get()
        self.bank.delete_account(password)

    def withdraw(self):
        account_id = self.account_id_entry.get()
        password = self.password_entry.get()
        amount = self.amount_entry.get()
        self.bank.withdraw_amount(account_id, password, amount)
    def deposit(self):
        account_id = self.account_id_entry.get()
        password = self.password_entry.get()
        amount = self.amount_entry.get()
        self.bank.deposit_amount(account_id, password, amount)
    def transfer(self):
        account_id = self.account_id_entry.get()
        password = self.password_entry.get()
        amount = self.amount_entry.get()
        self.bank.transfer_amount(account_id, password, amount)
    
    