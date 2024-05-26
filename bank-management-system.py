import sqlite3 as sq

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
        self.conn.commit()

    def create_account(self, account_id, password, email, phone, address, balance):
        self.cur.execute('INSERT INTO bank VALUES (?, ?, ?, ?, ?, ?)', (account_id, password, email, phone, address, balance))
        self.conn.commit()

    def view_account(self, password):
        self.cur.execute('SELECT * FROM bank WHERE password=?', (password,))
        data = self.cur.fetchall()
        return data

    def delete_account(self, password):
        self.cur.execute('DELETE FROM bank WHERE password=?', (password,))
        self.conn.commit()

    def update_account(self, account_id, password, email, phone, address, balance):
        self.cur.execute('UPDATE bank SET account_id=?, password=?, email=?, phone=?, address=? WHERE password=?', (account_id, password, email, phone, address, password))
        self.conn.commit()

    def deposit_amount(self, amount, account_id, password):
        self.cur.execute('SELECT balance FROM bank WHERE password=?', (password,))
        balance = self.cur.fetchone()[0]
        new_balance = balance + amount
        self.cur.execute('UPDATE bank SET balance=? WHERE password=?', (new_balance, password))
        self.conn.commit()
        self.record_transaction_detail(account_id, "deposit", amount, f"{account_id} deposit amount {amount} successfully")

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
        self.cur.execute('SELECT balance FROM bank WHERE account_id=?', (account_id,))
        balance = self.cur.fetchone()[0]
        return balance

    def record_transaction_detail(self, account_id, transaction_type, transaction_amount, description):
        self.cur.execute('INSERT INTO transaction_history (account_id, transaction_type, amount, transaction_date, description) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)', (account_id, transaction_type, transaction_amount, description))
        self.conn.commit()

    def transaction_history(self, account_id):
        self.cur.execute('SELECT * FROM transaction_history WHERE account_id=?', (account_id,))
        data = self.cur.fetchall()
        return data
