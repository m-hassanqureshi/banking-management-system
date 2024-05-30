import sqlite3 as sq
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

class DataBaseTasks:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sq.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS bank_users
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
                             FOREIGN KEY (account_id) REFERENCES bank_users(account_id));''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS bank_admins
                            (username VARCHAR(15),
                             password VARCHAR(12));''')
        self.conn.commit()

    def create_account(self, account_id, password, email, phone, address, balance):
        try:
            self.cur.execute('INSERT INTO bank_users VALUES (?, ?, ?, ?, ?, ?)', (account_id, password, email, phone, address, balance))
            self.conn.commit()
        except sq.IntegrityError:
            messagebox.showerror("Error", "Account ID already exists")

    def view_account(self, account_id):
        self.cur.execute('SELECT * FROM bank_users WHERE account_id=?', (account_id,))
        data = self.cur.fetchall()
        return data

    def delete_account(self, account_id):
        self.cur.execute('DELETE FROM bank_users WHERE account_id=?', (account_id,))
        self.conn.commit()

    def update_account(self, account_id, password, email, phone, address, balance):
        self.cur.execute('UPDATE bank_users SET password=?, email=?, phone=?, address=?, balance=? WHERE account_id=?', (password, email, phone, address, balance, account_id))
        self.conn.commit()

    def deposit_amount(self, amount, account_id):
        self.cur.execute('SELECT balance FROM bank_users WHERE account_id=?', (account_id,))
        balance = self.cur.fetchone()[0]
        new_balance = balance + amount
        self.cur.execute('UPDATE bank_users SET balance=? WHERE account_id=?', (new_balance, account_id))
        self.conn.commit()
        self.record_transaction_detail(account_id, "deposit", amount, f"{account_id} deposited amount {amount} successfully")

    def withdraw_amount(self, account_id, amount):
        self.cur.execute('SELECT balance FROM bank_users WHERE account_id=?', (account_id,))
        balance = self.cur.fetchone()[0]
        new_balance = balance - amount
        self.cur.execute('UPDATE bank_users SET balance=? WHERE account_id=?', (new_balance, account_id))
        self.conn.commit()
        self.record_transaction_detail(account_id, "withdrawal", amount, f"{account_id} withdrew amount {amount} successfully")

    def transfer_amount(self, sender_account_id, receiver_account_id, amount):
        self.cur.execute('SELECT balance FROM bank_users WHERE account_id=?', (sender_account_id,))
        sender_balance = self.cur.fetchone()[0]
        new_sender_balance = sender_balance - amount
        self.cur.execute('UPDATE bank_users SET balance=? WHERE account_id=?', (new_sender_balance, sender_account_id))
        self.cur.execute('SELECT balance FROM bank_users WHERE account_id=?', (receiver_account_id,))
        receiver_balance = self.cur.fetchone()[0]
        new_receiver_balance = receiver_balance + amount
        self.cur.execute('UPDATE bank_users SET balance=? WHERE account_id=?', (new_receiver_balance, receiver_account_id))
        self.conn.commit()
        self.record_transaction_detail(sender_account_id, "transfer", amount, f"{sender_account_id} transferred amount {amount} to {receiver_account_id} successfully")
        self.record_transaction_detail(receiver_account_id, "transfer", amount, f"{receiver_account_id} received amount {amount} from {sender_account_id} successfully")

    def view_balance(self, account_id):
        self.cur.execute('SELECT balance FROM bank_users WHERE account_id=?', (account_id,))
        balance = self.cur.fetchone()[0]
        return balance

    def record_transaction_detail(self, account_id, transaction_type, transaction_amount, description):
        self.cur.execute('INSERT INTO transaction_history (account_id, transaction_type, amount, transaction_date, description) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)', (account_id, transaction_type, transaction_amount, description))
        self.conn.commit()

    def transaction_history(self, account_id):
        self.cur.execute('SELECT * FROM transaction_history WHERE account_id=?', (account_id,))
        data = self.cur.fetchall()
        return data

    def get_password(self, account_id):
        self.cur.execute('SELECT password FROM bank_users WHERE account_id=?', (account_id,))
        password = self.cur.fetchone()[0]
        return password

    def get_account_id(self, password):
        self.cur.execute('SELECT account_id FROM bank_users WHERE password=?', (password,))
        account_id = self.cur.fetchone()[0]
        return account_id

    def get_admin_username(self, password):
        self.cur.execute('SELECT username FROM bank_admins WHERE password=?', (password,))
        username = self.cur.fetchone()[0]
        return username

    def get_admin_password(self, username):
        self.cur.execute('SELECT password FROM bank_admins WHERE username=?', (username,))
        password = self.cur.fetchone()[0]
        return password

    def close_connection(self):
        self.conn.close()

class Bank:
    def __init__(self):
        self.db = DataBaseTasks('bank.db')

    def admin_login(self, username, password):
        stored_admin_username = self.db.get_admin_username(password)
        stored_admin_password = self.db.get_admin_password(username)
        if stored_admin_password is not None and stored_admin_password == password and stored_admin_username is not None and stored_admin_username == username:
            return True
        else:
            return False

    def authentication(self, account_id, password):
        stored_id = self.db.get_account_id(password)
        stored_password = self.db.get_password(account_id)
        if stored_password is not None and stored_password == password and stored_id is not None and stored_id == account_id:
            return True
        else:
            return False

    def create_account(self, account_id, password, email, phone, address, balance, admin_username, admin_password):
        if self.admin_login(admin_username, admin_password):
            self.db.create_account(account_id, password, email, phone, address, balance)
        else:
            messagebox.showerror("Error", "Invalid Admin Username or Password")

    def view_account(self, account_id, password):
        if self.authentication(account_id, password):
            return self.db.view_account(account_id)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")
            return None

    def delete_account(self, account_id, admin_username, admin_password):
        if self.admin_login(admin_username, admin_password):
            self.db.delete_account(account_id)
        else:
            messagebox.showerror("Error", "Invalid Admin Username or Password")

    def update_account(self, account_id, password, email, phone, address, balance):
        if self.authentication(account_id, password):
            self.db.update_account(account_id, password, email, phone, address, balance)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")

    def deposit_amount(self, amount, account_id, password):
        if self.authentication(account_id, password):
            self.db.deposit_amount(amount, account_id)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")

    def withdraw_amount(self, account_id, password, amount):
        if self.authentication(account_id, password):
            self.db.withdraw_amount(account_id, amount)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")

    def transfer_amount(self, sender_account_id, password, receiver_account_id, amount):
        if self.authentication(sender_account_id, password):
            self.db.transfer_amount(sender_account_id, receiver_account_id, amount)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")

    def view_balance(self, account_id, password):
        if self.authentication(account_id, password):
            return self.db.view_balance(account_id)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")
            return None

    def record_transaction_detail(self, account_id, password, transaction_type, transaction_amount, description):
        if self.authentication(account_id, password):
            self.db.record_transaction_detail(account_id, transaction_type, transaction_amount, description)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")

    def transaction_history(self, account_id, password):
        if self.authentication(account_id, password):
            return self.db.transaction_history(account_id)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")
            return None

class App:
    def __init__(self, master):
        self.master = master
        self.bank = Bank()
        self.is_admin = False
        self.master.title("Bank Management System")
        self.master.geometry("500x400")
        self.master.configure(bg="#1a1a2e")
        self.create_widgets()

    def create_widgets(self):
        self.master.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.master, text="Bank Management System", font=("Helvetica", 24), text_color="white")
        self.title_label.grid(row=0, column=0, columnspan=3, pady=20)

        self.account_id_label = ctk.CTkLabel(self.master, text="Account ID:", font=("Helvetica", 14), text_color="white")
        self.account_id_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")

        self.account_id_entry = ctk.CTkEntry(self.master, font=("Helvetica", 14))
        self.account_id_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        self.password_label = ctk.CTkLabel(self.master, text="Password:", font=("Helvetica", 14), text_color="white")
        self.password_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")

        self.password_entry = ctk.CTkEntry(self.master, font=("Helvetica", 14), show="*")
        self.password_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        self.login_button = ctk.CTkButton(self.master, text="Login", command=self.login, font=("Helvetica", 14))
        self.login_button.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.admin_login_button = ctk.CTkButton(self.master, text="Admin Login", command=self.admin_login, font=("Helvetica", 14))
        self.admin_login_button.grid(row=3, column=1, padx=20, pady=10, sticky="e")

    def login(self):
        account_id = self.account_id_entry.get()
        password = self.password_entry.get()
        if self.bank.authentication(account_id, password):
            self.user_window(account_id, password)
        else:
            messagebox.showerror("Error", "Invalid Account ID or Password")

    def admin_login(self):
        self.admin_login_window = ctk.CTkToplevel(self.master)
        self.admin_login_window.title("Admin Login")
        self.admin_login_window.geometry("400x300")
        self.admin_login_window.configure(bg="#1a1a2e")

        self.admin_username_label = ctk.CTkLabel(self.admin_login_window, text="Username:", font=("Helvetica", 14))
        self.admin_username_label.grid(row=0, column=0, padx=20, pady=10, sticky="e")

        self.admin_username_entry = ctk.CTkEntry(self.admin_login_window, font=("Helvetica", 14))
        self.admin_username_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        self.admin_password_label = ctk.CTkLabel(self.admin_login_window, text="Password:", font=("Helvetica", 14))
        self.admin_password_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")

        self.admin_password_entry = ctk.CTkEntry(self.admin_login_window, font=("Helvetica", 14), show="*")
        self.admin_password_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        self.admin_login_button = ctk.CTkButton(self.admin_login_window, text="Login", command=self.check_admin_login, font=("Helvetica", 14))
        self.admin_login_button.grid(row=2, column=1, padx=20, pady=10, sticky="w")

    def check_admin_login(self):
        username = self.admin_username_entry.get()
        password = self.admin_password_entry.get()
        if self.bank.admin_login(username, password):
            self.is_admin = True
            self.admin_window()
            self.admin_login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid Admin Username or Password")

    def admin_window(self):
        admin_window = ctk.CTkToplevel(self.master)
        admin_window.title("Admin Panel")
        admin_window.geometry("500x400")
        admin_window.configure(bg="#1a1a2e")

        self.create_acc_button = ctk.CTkButton(admin_window, text="Create Account", command=self.create_account_window, font=("Helvetica", 14))
        self.create_acc_button.grid(row=0, column=0, padx=20, pady=10)

        self.delete_acc_button = ctk.CTkButton(admin_window, text="Delete Account", command=self.delete_account_window, font=("Helvetica", 14))
        self.delete_acc_button.grid(row=0, column=1, padx=20, pady=10)

    def create_account_window(self):
        create_window = ctk.CTkToplevel(self.master)
        create_window.title("Create Account")
        create_window.geometry("500x500")
        create_window.configure(bg="#1a1a2e")

        self.new_acc_id_label = ctk.CTkLabel(create_window, text="Account ID:", font=("Helvetica", 14))
        self.new_acc_id_label.grid(row=0, column=0, padx=20, pady=10, sticky="e")

        self.new_acc_id_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14))
        self.new_acc_id_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        self.new_acc_password_label = ctk.CTkLabel(create_window, text="Password:", font=("Helvetica", 14))
        self.new_acc_password_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")

        self.new_acc_password_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14), show="*")
        self.new_acc_password_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        self.new_acc_email_label = ctk.CTkLabel(create_window, text="Email:", font=("Helvetica", 14))
        self.new_acc_email_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")

        self.new_acc_email_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14))
        self.new_acc_email_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        self.new_acc_phone_label = ctk.CTkLabel(create_window, text="Phone:", font=("Helvetica", 14))
        self.new_acc_phone_label.grid(row=3, column=0, padx=20, pady=10, sticky="e")

        self.new_acc_phone_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14))
        self.new_acc_phone_entry.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.new_acc_address_label = ctk.CTkLabel(create_window, text="Address:", font=("Helvetica", 14))
        self.new_acc_address_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")

        self.new_acc_address_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14))
        self.new_acc_address_entry.grid(row=4, column=1, padx=20, pady=10, sticky="w")

        self.new_acc_balance_label = ctk.CTkLabel(create_window, text="Balance:", font=("Helvetica", 14))
        self.new_acc_balance_label.grid(row=5, column=0, padx=20, pady=10, sticky="e")

        self.new_acc_balance_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14))
        self.new_acc_balance_entry.grid(row=5, column=1, padx=20, pady=10, sticky="w")

        self.admin_username_label = ctk.CTkLabel(create_window, text="Admin Username:", font=("Helvetica", 14))
        self.admin_username_label.grid(row=6, column=0, padx=20, pady=10, sticky="e")

        self.admin_username_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14))
        self.admin_username_entry.grid(row=6, column=1, padx=20, pady=10, sticky="w")

        self.admin_password_label = ctk.CTkLabel(create_window, text="Admin Password:", font=("Helvetica", 14))
        self.admin_password_label.grid(row=7, column=0, padx=20, pady=10, sticky="e")

        self.admin_password_entry = ctk.CTkEntry(create_window, font=("Helvetica", 14), show="*")
        self.admin_password_entry.grid(row=7, column=1, padx=20, pady=10, sticky="w")

        self.create_button = ctk.CTkButton(create_window, text="Create", command=self.create_account, font=("Helvetica", 14))
        self.create_button.grid(row=8, column=1, padx=20, pady=10, sticky="w")

    def create_account(self):
        account_id = self.new_acc_id_entry.get()
        password = self.new_acc_password_entry.get()
        email = self.new_acc_email_entry.get()
        phone = self.new_acc_phone_entry.get()
        address = self.new_acc_address_entry.get()
        balance = int(self.new_acc_balance_entry.get())
        admin_username = self.admin_username_entry.get()
        admin_password = self.admin_password_entry.get()
        self.bank.create_account(account_id, password, email, phone, address,
