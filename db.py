import sqlite3,phonenumbers,datetime,random

LOCAL_DB = "slack.sqlite"

def init_db():
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS orders (order_id varchar(255) UNIQUE, customer_id INTEGER, user, date, comment)")
    conn.commit()
    conn.close()

def new_order():
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    order_id = "#zp%s" % random.randint(100,999)
    data = (order_id,19221,"@tomasz",datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S"),"zamówienie od klienta")
    c.execute("INSERT INTO orders VALUES (?,?,?,?,?)", data)
    conn.commit()
    order = get_order(order_id)
    conn.close()
    return order

def orders_list():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    data = []
    rows = c.fetchall()
    for row in rows:
        row = dict(zip(row.keys(), row))
        data.append(row)
    conn.close()
    return data

def get_order(order_id):
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id='%s'" % order_id)
    data = []
    row = c.fetchone()
    row = dict(zip(row.keys(), row))
    conn.close()
    return row

def delete_order(order_id):
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE order_id='%s'" % order_id)
    conn.commit()
    conn.close()

