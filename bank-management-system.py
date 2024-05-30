import sqlite3 as sq
import tkinter as tk
from tkinter import messagebox,ttk
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
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        
        self.role_label = ctk.CTkLabel(self.master, text="Login as:", font=("Helvetica", 16))
        self.role_label.grid(row=0, column=0, padx=20, pady=20, sticky="W")

        self.role_var = ctk.StringVar(value="user")
        self.user_radio = ctk.CTkRadioButton(self.master, text="User", variable=self.role_var, value="user", command=self.update_role)
        self.user_radio.grid(row=0, column=1, padx=10, pady=20, sticky="W")

        self.admin_radio = ctk.CTkRadioButton(self.master, text="Admin", variable=self.role_var, value="admin", command=self.update_role)
        self.admin_radio.grid(row=0, column=2, padx=10, pady=20, sticky="W")

        self.account_label = ctk.CTkLabel(self.master, text="Account ID:", font=("Helvetica", 14))
        self.account_label.grid(row=1, column=0, padx=20, pady=10, sticky="W")

        self.account_entry = ctk.CTkEntry(self.master, font=("Helvetica", 14))
        self.account_entry.grid(row=1, column=1, padx=20, pady=10, columnspan=2, sticky="WE")

        self.password_label = ctk.CTkLabel(self.master, text="Password:", font=("Helvetica", 14))
        self.password_label.grid(row=2, column=0, padx=20, pady=10, sticky="W")

        self.password_entry = ctk.CTkEntry(self.master, show="*", font=("Helvetica", 14))
        self.password_entry.grid(row=2, column=1, padx=20, pady=10, columnspan=2, sticky="WE")

        self.login_button = ctk.CTkButton(self.master, text="Login", command=self.login, font=("Helvetica", 14))
        self.login_button.grid(row=3, column=0, padx=20, pady=20, columnspan=3)

    def update_role(self):
        self.is_admin = self.role_var.get() == "admin"
        self.account_label.configure(text="Username:" if self.is_admin else "Account ID:")

    def login(self):
        account_id = self.account_entry.get()
        password = self.password_entry.get()
        if self.is_admin:
            if self.bank.admin_login(account_id, password):
                self.admin_window()
            else:
                messagebox.showerror("Error", "Invalid Admin Username or Password")
        else:
            if self.bank.authentication(account_id, password):
                self.user_window(account_id, password)
            else:
                messagebox.showerror("Error", "Invalid Account ID or Password")

    def admin_window(self):
        admin_window = ctk.CTkToplevel(self.master)
        admin_window.title("Admin Panel")
        admin_window.geometry("400x200")
        admin_window.configure(bg="#1a1a2e")

        self.create_acc_button = ctk.CTkButton(admin_window, text="Create Account", command=self.create_account, font=("Helvetica", 14))
        self.create_acc_button.grid(row=0, column=0, padx=20, pady=10)

        self.delete_acc_button = ctk.CTkButton(admin_window, text="Delete Account", command=self.delete_account, font=("Helvetica", 14))
        self.delete_acc_button.grid(row=0, column=1, padx=20, pady=10)

    def user_window(self, account_id, password):
        user_window = ctk.CTkToplevel(self.master)
        user_window.title("User Panel")
        user_window.geometry("500x400")
        user_window.configure(bg="#1a1a2e")

        self.view_bal_button = ctk.CTkButton(user_window, text="View Balance", command=lambda: self.view_balance(account_id, password), font=("Helvetica", 14))
        self.view_bal_button.grid(row=0, column=0, padx=20, pady=10)

        self.deposit_button = ctk.CTkButton(user_window, text="Deposit Amount", command=lambda: self.deposit_amount(account_id, password), font=("Helvetica", 14))
        self.deposit_button.grid(row=0, column=1, padx=20, pady=10)

        self.withdraw_button = ctk.CTkButton(user_window, text="Withdraw Amount", command=lambda: self.withdraw_amount(account_id, password), font=("Helvetica", 14))
        self.withdraw_button.grid(row=0, column=2, padx=20, pady=10)

        self.transfer_button = ctk.CTkButton(user_window, text="Transfer Amount", command=lambda: self.transfer_amount(account_id, password), font=("Helvetica", 14))
        self.transfer_button.grid(row=1, column=0, padx=20, pady=10)

        self.view_trans_hist_button = ctk.CTkButton(user_window, text="View Transaction History", command=lambda: self.view_transaction_history(account_id, password), font=("Helvetica", 14))
        self.view_trans_hist_button.grid(row=1, column=1, padx=20, pady=10)
    
        self.view_acc_button = ctk.CTkButton(user_window, text="View Account Details", command=lambda: self.view_account_details(account_id, password), font=("Helvetica", 14))
        self.view_acc_button.grid(row=1, column=2, padx=20, pady=10)
    
        self.update_acc_button = ctk.CTkButton(user_window, text="Update Account Information", command=lambda: self.update_account_info(account_id, password), font=("Helvetica", 14))
        self.update_acc_button.grid(row=2, column=0, padx=20, pady=10)

    def create_account(self):
        def create():
            account_id = account_id_entry.get()
            password = password_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            address = address_entry.get()
            balance = float(balance_entry.get())
            admin_username = self.account_entry.get()
            admin_password = self.password_entry.get()
            self.bank.create_account(account_id, password, email, phone, address, balance, admin_username, admin_password)
            create_acc_window.destroy()

        create_acc_window = ctk.CTkToplevel(self.master)
        create_acc_window.title("Create Account")
        create_acc_window.geometry("400x350")
        create_acc_window.configure(bg="#1a1a2e")

        ctk.CTkLabel(create_acc_window, text="Account ID:", font=("Helvetica", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        account_id_entry = ctk.CTkEntry(create_acc_window, font=("Helvetica", 14))
        account_id_entry.grid(row=0, column=1, padx=20, pady=10)

        ctk.CTkLabel(create_acc_window, text="Password:", font=("Helvetica", 14)).grid(row=1, column=0, padx=20, pady=10, sticky="W")
        password_entry = ctk.CTkEntry(create_acc_window, show="*", font=("Helvetica", 14))
        password_entry.grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkLabel(create_acc_window, text="Email:", font=("Helvetica", 14)).grid(row=2, column=0, padx=20, pady=10, sticky="W")
        email_entry = ctk.CTkEntry(create_acc_window, font=("Helvetica", 14))
        email_entry.grid(row=2, column=1, padx=20, pady=10)

        ctk.CTkLabel(create_acc_window, text="Phone:", font=("Helvetica", 14)).grid(row=3, column=0, padx=20, pady=10, sticky="W")
        phone_entry = ctk.CTkEntry(create_acc_window, font=("Helvetica", 14))
        phone_entry.grid(row=3, column=1, padx=20, pady=10)

        ctk.CTkLabel(create_acc_window, text="Address:", font=("Helvetica", 14)).grid(row=4, column=0, padx=20, pady=10, sticky="W")
        address_entry = ctk.CTkEntry(create_acc_window, font=("Helvetica", 14))
        address_entry.grid(row=4, column=1, padx=20, pady=10)

        ctk.CTkLabel(create_acc_window, text="Balance:", font=("Helvetica", 14)).grid(row=5, column=0, padx=20, pady=10, sticky="W")
        balance_entry = ctk.CTkEntry(create_acc_window, font=("Helvetica", 14))
        balance_entry.grid(row=5, column=1, padx=20, pady=10)

        create_button = ctk.CTkButton(create_acc_window, text="Create", command=create, font=("Helvetica", 14))
        create_button.grid(row=6, column=0, padx=20, pady=20, columnspan=2)

    def delete_account(self):
        def delete():
            account_id = account_id_entry.get()
            admin_username = self.account_entry.get()
            admin_password = self.password_entry.get()
            self.bank.delete_account(account_id, admin_username, admin_password)
            delete_acc_window.destroy()

        delete_acc_window = ctk.CTkToplevel(self.master)
        delete_acc_window.title("Delete Account")
        delete_acc_window.geometry("300x150")
        delete_acc_window.configure(bg="#1a1a2e")

        ctk.CTkLabel(delete_acc_window, text="Account ID:", font=("Helvetica", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        account_id_entry = ctk.CTkEntry(delete_acc_window, font=("Helvetica", 14))
        account_id_entry.grid(row=0, column=1, padx=20, pady=10)

        delete_button = ctk.CTkButton(delete_acc_window, text="Delete", command=delete, font=("Helvetica", 14))
        delete_button.grid(row=1, column=0, padx=20, pady=20, columnspan=2)
    def view_account_details(self, account_id, password):
        account_info = self.bank.view_account(account_id, password)
        if account_info:
            info_window = ctk.CTkToplevel(self.master)
            info_window.title("Account Details")
            info_window.geometry("400x300")
            info_window.configure(bg="#1a1a2e")        
            info_labels = ["Account ID:", "Password:", "Email:", "Phone:", "Address:", "Balance:"]
            for i, info in enumerate(account_info[0]):
                ctk.CTkLabel(info_window, text=f"{info_labels[i]} {info}", font=("Helvetica", 14)).grid(row=i, column=0, padx=20, pady=10, sticky="W")

def update_account_info(self, account_id, password):
    account_info = self.bank.view_account(account_id, password)
    if account_info:
        def update():
            new_password = password_entry.get()
            new_email = email_entry.get()
            new_phone = phone_entry.get()
            new_address = address_entry.get()
            new_balance = float(balance_entry.get())
            self.bank.update_account(account_id, new_password, new_email, new_phone, new_address, new_balance)
            update_window.destroy()
        update_window = ctk.CTkToplevel(self.master)
        update_window.title("Update Account Information")
        update_window.geometry("400x400")
        update_window.configure(bg="#1a1a2e")
        ctk.CTkLabel(update_window, text="Password:", font=("Helvetica", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        password_entry = ctk.CTkEntry(update_window, font=("Helvetica", 14))
        password_entry.insert(0, account_info[0][1])
        password_entry.grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkLabel(update_window, text="Email:", font=("Helvetica", 14)).grid(row=1, column=0, padx=20, pady=10, sticky="W")
        email_entry = ctk.CTkEntry(update_window, font=("Helvetica", 14))
        email_entry.insert(0, account_info[0][2])
        email_entry.grid(row=1, column=1, padx=20, pady=10)
        ctk.CTkLabel(update_window, text="Phone:", font=("Helvetica", 14)).grid(row=2, column=0, padx=20, pady=10, sticky="W")
        phone_entry = ctk.CTkEntry(update_window, font=("Helvetica", 14))
        phone_entry.insert(0, account_info[0][3])
        phone_entry.grid(row=2, column=1, padx=20, pady=10)
        ctk.CTkLabel(update_window, text="Address:", font=("Helvetica", 14)).grid(row=3, column=0, padx=20, pady=10, sticky="W")
        address_entry = ctk.CTkEntry(update_window, font=("Helvetica", 14))
        address_entry.insert(0, account_info[0][4])
        address_entry.grid(row=3, column=1, padx=20, pady=10)
        ctk.CTkLabel(update_window, text="Balance:", font=("Helvetica", 14)).grid(row=4, column=0, padx=20, pady=10, sticky="W")
        balance_entry = ctk.CTkEntry(update_window, font=("Helvetica", 14))
        balance_entry.insert(0, account_info[0][5])
        balance_entry.grid(row=4, column=1, padx=20, pady=10)
        update_button = ctk.CTkButton(update_window, text="Update", command=update, font=("Helvetica", 14))
        update_button.grid(row=5, column=0, padx=20, pady=20, columnspan=2)

    def deposit_amount(self, account_id, password):
        def deposit():
            amount = float(amount_entry.get())
            self.bank.deposit_amount(amount, account_id, password)
            deposit_window.destroy()
        deposit_window = ctk.CTkToplevel(self.master)
        deposit_window.title("Deposit Amount")
        deposit_window.geometry("300x150")
        deposit_window.configure(bg="#1a1a2e")
        ctk.CTkLabel(deposit_window, text="Amount:", font=("Helvetica", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        amount_entry = ctk.CTkEntry(deposit_window, font=("Helvetica", 14))
        amount_entry.grid(row=0, column=1, padx=20, pady=10)
        deposit_button = ctk.CTkButton(deposit_window, text="Deposit", command=deposit, font=("Helvetica", 14))
        deposit_button.grid(row=1, column=0, padx=20, pady=20, columnspan=2)

    def withdraw_amount(self, account_id, password):
        def withdraw():
            amount = float(amount_entry.get())
            self.bank.withdraw_amount(account_id, password, amount)
            withdraw_window.destroy()
        withdraw_window = ctk.CTkToplevel(self.master)
        withdraw_window.title("Withdraw Amount")
        withdraw_window.geometry("300x150")
        withdraw_window.configure(bg="#1a1a2e")
        ctk.CTkLabel(withdraw_window, text="Amount:", font=("Helvetica", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        amount_entry = ctk.CTkEntry(withdraw_window, font=("Helvetica", 14))
        amount_entry.grid(row=0, column=1, padx=20, pady=10)
        withdraw_button = ctk.CTkButton(withdraw_window, text="Withdraw", command=withdraw, font=("Helvetica", 14))
        withdraw_button.grid(row=1, column=0, padx=20, pady=20, columnspan=2)

    def transfer_amount(self, account_id, password):
        def transfer():
            receiver_account_id = receiver_account_id_entry.get()
            amount = float(amount_entry.get())
            self.bank.transfer_amount(account_id, password, receiver_account_id, amount)
            transfer_window.destroy()
        transfer_window = ctk.CTkToplevel(self.master)
        transfer_window.title("Transfer Amount")
        transfer_window.geometry("350x200")
        transfer_window.configure(bg="#1a1a2e")
        ctk.CTkLabel(transfer_window, text="Receiver Account ID:", font=("Helvetica", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="W")
        receiver_account_id_entry = ctk.CTkEntry(transfer_window, font=("Helvetica", 14))
        receiver_account_id_entry.grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkLabel(transfer_window, text="Amount:", font=("Helvetica", 14)).grid(row=1, column=0, padx=20, pady=10, sticky="W")
        amount_entry = ctk.CTkEntry(transfer_window, font=("Helvetica", 14))
        amount_entry.grid(row=1, column=1, padx=20, pady=10)
        transfer_button = ctk.CTkButton(transfer_window, text="Transfer", command=transfer, font=("Helvetica", 14))
        transfer_button.grid(row=2, column=0, padx=20, pady=20, columnspan=2)

    def view_balance(self, account_id, password):
        balance = self.bank.view_balance(account_id, password)
        messagebox.showinfo("Balance", f"Your balance is: {balance}")

    def view_transaction_history(self, account_id, password):
        transactions = self.bank.transaction_history(account_id, password)
        history_window = ctk.CTkToplevel(self.master)
        history_window.title("Transaction History")
        history_window.configure(bg="#1a1a2e")
        for i, transaction in enumerate(transactions):
            ctk.CTkLabel(history_window, text=f"Date: {transaction[3]}, Type: {transaction[1]}, Amount: {transaction[2]}, Description: {transaction[4]}", font=("Helvetica", 12)).grid(row=i, column=0, padx=20, pady=10)

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
