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
                            (admin_name VARCHAR(15),
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

    def get_admin_name(self, password):
        self.cur.execute('SELECT admin_name FROM bank_admins WHERE password=?', (password,))
        admin_name = self.cur.fetchone()[0]
        return admin_name

    def get_admin_password(self, admin_name):
        self.cur.execute('SELECT password FROM bank_admins WHERE admin_name=?', (admin_name,))
        password = self.cur.fetchone()[0]
        return password

    def close_connection(self):
        self.conn.close()

class Bank:
    def __init__(self):
        self.db = DataBaseTasks('bank.db')

    def admin_login(self, admin_name, password):
        stored_admin_name = self.db.get_admin_name(password)
        stored_admin_password = self.db.get_admin_password(admin_name)
        if stored_admin_password is not None and stored_admin_password == password and stored_admin_name is not None and stored_admin_name == admin_name:
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

    def create_account(self, account_id, password, email, phone, address, balance, admin_admin_name, admin_password):
        if self.admin_login(admin_name, admin_password):
            self.db.create_account(account_id, password, email, phone, address, balance)
        else:
            messagebox.showerror("Error", "Invalid Admin admin_name or Password")

    def view_account(self, account_id, password):
        if self.authentication(account_id, password):
            return self.db.view_account(account_id)
        else:
            messagebox.showerror("Error", "Invalid Account Id or Password")
            return None

    def delete_account(self, account_id, admin_name, admin_password):
        if self.admin_login(admin_name, admin_password):
            self.db.delete_account(account_id)
        else:
            messagebox.showerror("Error", "Invalid Admin admin_name or Password")

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
        self.master.configure(bg="#2c3e50")
        self.create_widgets()

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def create_widgets(self):
        self.master.grid_columnconfigure(1, weight=1)
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.role_label = ctk.CTkLabel(self.master, text="Login as:")
        self.role_label.grid(row=0, column=0, padx=10, pady=20, sticky="W")

        self.role_var = ctk.StringVar(value="user")
        self.user_radio = ctk.CTkRadioButton(self.master, text="User", variable=self.role_var, value="user", command=self.update_role)
        self.user_radio.grid(row=0, column=1, padx=10, pady=20, sticky="W")

        self.admin_radio = ctk.CTkRadioButton(self.master, text="Admin", variable=self.role_var, value="admin", command=self.update_role)
        self.admin_radio.grid(row=0, column=2, padx=10, pady=20, sticky="W")

        self.account_label = ctk.CTkLabel(self.master, text="Account ID:")
        self.account_label.grid(row=1, column=0, padx=10, pady=10, sticky="W")

        self.account_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        self.account_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2, sticky="WE")

        self.password_label = ctk.CTkLabel(self.master, text="Password:")
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="W")

        self.password_entry = ctk.CTkEntry(self.master, show="*", font=("Arial", 12))
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=2, sticky="WE")

        self.login_button = ctk.CTkButton(self.master, text="Login", command=self.login)
        self.login_button.grid(row=3, column=0, padx=10, pady=20, columnspan=3)

    def update_role(self):
        self.is_admin = self.role_var.get() == "admin"
        self.account_label.configure(text="Name:" if self.is_admin else "Account ID:")

    def login(self):
        account_id = self.account_entry.get()
        password = self.password_entry.get()
        if self.is_admin:
            if self.bank.admin_login(account_id, password):
                self.admin_window()
            else:
                messagebox.showerror("Error", "Invalid  admin_name or Password")
        else:
            if self.bank.authentication(account_id, password):
                self.user_window(account_id, password)
            else:
                messagebox.showerror("Error", "Invalid Account ID or Password")

    def admin_window(self):
        self.clear_window()

        self.create_acc_button = ctk.CTkButton(self.master, text="Create Account", command=self.create_account)
        self.create_acc_button.grid(row=0, column=0, padx=10, pady=10)

        self.delete_acc_button = ctk.CTkButton(self.master, text="Delete Account", command=self.delete_account)
        self.delete_acc_button.grid(row=0, column=1, padx=10, pady=10)

        self.back_button = ctk.CTkButton(self.master, text="Back", command=self.create_widgets)
        self.back_button.grid(row=1, column=0, padx=10, pady=20, columnspan=2)

    def user_window(self, account_id, password):
        self.clear_window()

        self.view_bal_button = ctk.CTkButton(self.master, text="View Balance", command=lambda: self.view_balance(account_id, password))
        self.view_bal_button.grid(row=0, column=0, padx=10, pady=10)

        self.deposit_button = ctk.CTkButton(self.master, text="Deposit Amount", command=lambda: self.deposit_amount(account_id, password))
        self.deposit_button.grid(row=0, column=1, padx=10, pady=10)

        self.withdraw_button = ctk.CTkButton(self.master, text="Withdraw Amount", command=lambda: self.withdraw_amount(account_id, password))
        self.withdraw_button.grid(row=0, column=2, padx=10, pady=10)

        self.transfer_button = ctk.CTkButton(self.master, text="Transfer Amount", command=lambda: self.transfer_amount(account_id, password))
        self.transfer_button.grid(row=1, column=0, padx=10, pady=10)

        self.view_trans_hist_button = ctk.CTkButton(self.master, text="View Transaction History", command=lambda: self.view_transaction_history(account_id, password))
        self.view_trans_hist_button.grid(row=1, column=1, padx=10, pady=10)

        self.view_acc_button = ctk.CTkButton(self.master, text="View Account Info", command=lambda: self.view_account(account_id, password))
        self.view_acc_button.grid(row=2, column=0, padx=10, pady=10)

        self.update_acc_button = ctk.CTkButton(self.master, text="Update Account Info", command=lambda: self.update_account(account_id, password))
        self.update_acc_button.grid(row=2, column=1, padx=10, pady=10)

        self.back_button = ctk.CTkButton(self.master, text="Back", command=self.create_widgets)
        self.back_button.grid(row=3, column=0, padx=10, pady=20, columnspan=3)

    def create_account(self):
        self.clear_window()

        ctk.CTkLabel(self.master, text="Account ID:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        account_id_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        account_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.master, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky="W")
        password_entry = ctk.CTkEntry(self.master, show="*", font=("Arial", 12))
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.master, text="Email:").grid(row=2, column=0, padx=10, pady=10, sticky="W")
        email_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        email_entry.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.master, text="Phone:").grid(row=3, column=0, padx=10, pady=10, sticky="W")
        phone_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        phone_entry.grid(row=3, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.master, text="Address:").grid(row=4, column=0, padx=10, pady=10, sticky="W")
        address_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        address_entry.grid(row=4, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.master, text="Balance:").grid(row=5, column=0, padx=10, pady=10, sticky="W")
        balance_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        balance_entry.grid(row=5, column=1, padx=10, pady=10)

        create_button = ctk.CTkButton(self.master, text="Create", command=lambda: self.bank.create_account(
            account_id_entry.get(), password_entry.get(), email_entry.get(), phone_entry.get(), address_entry.get(),
            float(balance_entry.get()), self.account_entry.get(), self.password_entry.get()
        ))
        create_button.grid(row=6, column=0, padx=10, pady=20, columnspan=2)

        self.back_button = ctk.CTkButton(self.master, text="Back", command=self.admin_window)
        self.back_button.grid(row=7, column=0, padx=10, pady=20, columnspan=2)

    def delete_account(self):
        self.clear_window()

        ctk.CTkLabel(self.master, text="Account ID:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        account_id_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        account_id_entry.grid(row=0, column=1, padx=10, pady=10)

        delete_button = ctk.CTkButton(self.master, text="Delete", command=lambda: self.bank.delete_account(
            account_id_entry.get(), self.account_entry.get(), self.password_entry.get()
        ))
        delete_button.grid(row=1, column=0, padx=10, pady=20, columnspan=2)

        self.back_button = ctk.CTkButton(self.master, text="Back", command=self.admin_window)
        self.back_button.grid(row=2, column=0, padx=10, pady=20, columnspan=2)

    def deposit_amount(self, account_id, password):
        self.clear_window()

        ctk.CTkLabel(self.master, text="Amount to Deposit:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        amount_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        amount_entry.grid(row=0, column=1, padx=10, pady=10)

        deposit_button = ctk.CTkButton(self.master, text="Deposit", command=lambda: self.bank.deposit(account_id, password, float(amount_entry.get())))
        deposit_button.grid(row=1, column=0, padx=10, pady=20, columnspan=2)

        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=2, column=0, padx=10, pady=20, columnspan=2)

    def withdraw_amount(self, account_id, password):
        self.clear_window()

        ctk.CTkLabel(self.master, text="Amount to Withdraw:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        amount_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        amount_entry.grid(row=0, column=1, padx=10, pady=10)

        withdraw_button = ctk.CTkButton(self.master, text="Withdraw", command=lambda: self.bank.withdraw(account_id, password, float(amount_entry.get())))
        withdraw_button.grid(row=1, column=0, padx=10, pady=20, columnspan=2)

        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=2, column=0, padx=10, pady=20, columnspan=2)

    def transfer_amount(self, account_id, password):
        self.clear_window()

        ctk.CTkLabel(self.master, text="Recipient Account ID:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        recipient_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        recipient_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.master, text="Amount to Transfer:").grid(row=1, column=0, padx=10, pady=10, sticky="W")
        amount_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        amount_entry.grid(row=1, column=1, padx=10, pady=10)

        transfer_button = ctk.CTkButton(self.master, text="Transfer", command=lambda: self.bank.transfer(
            account_id, password, recipient_entry.get(), float(amount_entry.get())
        ))
        transfer_button.grid(row=2, column=0, padx=10, pady=20, columnspan=2)
        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=3, column=0, padx=10, pady=20, columnspan=2)
    def view_balance(self, account_id, password):
        self.clear_window()
        balance = self.bank.view_balance(account_id, password)
        balance_label = ctk.CTkLabel(self.master, text=f"Current Balance: {balance:.2f} PKR")
        balance_label.grid(row=0, column=0, padx=10, pady=20, columnspan=2)
        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=1, column=0, padx=10, pady=20, columnspan=2)
    def view_transaction_history(self, account_id, password):
        self.clear_window()
        transactions = self.bank.transaction_history(account_id, password)
        title_label = ctk.CTkLabel(self.master, text="Transaction History", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        for i, transaction in enumerate(transactions, start=1):
            transaction_label = ctk.CTkLabel(self.master, text=f"Date: {transaction[3]}, Type: {transaction[1]}, Amount: {transaction[2]}, Description: {transaction[4]}")
            transaction_label.grid(row=i, column=0, padx=10, pady=5, sticky="W", columnspan=2)
        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=i+1, column=0, padx=10, pady=20, columnspan=2)
    def update_account(self, account_id, password):
        self.clear_window()
        user_info = self.bank.view_account(account_id, password)
        if not user_info:
            messagebox.showerror("Error", "Failed to retrieve account info")
            self.user_window(account_id, password)
            return
        ctk.CTkLabel(self.master, text="Email:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        email_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        email_entry.insert(0, user_info[2])
        email_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(self.master, text="Phone:").grid(row=1, column=0, padx=10, pady=10, sticky="W")
        phone_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        phone_entry.insert(0, user_info[3])
        phone_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkLabel(self.master, text="Address:").grid(row=2, column=0, padx=10, pady=10, sticky="W")
        address_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        address_entry.insert(0, user_info[4])
        address_entry.grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkLabel(self.master, text="Balance:").grid(row=3, column=0, padx=10, pady=10, sticky="W")
        balance_entry = ctk.CTkEntry(self.master, font=("Arial", 12))
        balance_entry.insert(0, str(user_info[5]))
        balance_entry.grid(row=3, column=1, padx=10, pady=10)
        def update():
            self.bank.update_account(
            account_id, password, email_entry.get(), phone_entry.get(), address_entry.get(), float(balance_entry.get())
            )
            messagebox.showinfo("Update Account", "Account information updated successfully")
            self.user_window(account_id, password)
        update_button = ctk.CTkButton(self.master, text="Update", command=update)
        update_button.grid(row=4, column=0, padx=10, pady=20, columnspan=2)
        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=5, column=0, padx=10, pady=20, columnspan=2)
    def view_account(self, account_id, password):
        self.clear_window()
        account_details = self.bank.view_account(account_id, password)
        if account_details and len(account_details) >= 6:
            details = (
                f"Account ID: {account_details[0]}\n"
                f"Email: {account_details[2]}\n"
                f"Phone: {account_details[3]}\n"
                f"Address: {account_details[4]}\n"
                f"Balance: {account_details[5]}"
            )
            messagebox.showinfo("Account Details", details)
        else:
            messagebox.showerror("Error", "Failed to retrieve account details or incomplete data")
        self.back_button = ctk.CTkButton(self.master, text="Back", command=lambda: self.user_window(account_id, password))
        self.back_button.grid(row=1, column=0, padx=10, pady=20, columnspan=2)
if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
