import sqlite3

# THIS FUNCTION CONNECTS TO THE DATABASE 
def connect_db():
    conn = sqlite3.connect('ecommerce_platform.db')
    return conn

# THIS FUNCTION CREATES THE TABLE IN THE DATABASE 
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # product table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category_id INTEGER,
        subcategory_id INTEGER,
        stock_level INTEGER NOT NULL,
        warehouse_location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES Categories(category_id),
        FOREIGN KEY (subcategory_id) REFERENCES Subcategories(subcategory_id)
    )
    ''')

    # categories Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')

    # subcategories Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Subcategories (
        subcategory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (category_id) REFERENCES Categories(category_id)
    )
    ''')

    # inventory Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InventoryLogs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        change INTEGER NOT NULL,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )
    ''')

    # orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        status TEXT NOT NULL,
        total_price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
    )
    ''')

    # order Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        price_at_purchase REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Orders(order_id),
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )
    ''')

    # customers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        membership_tier TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # customer Profile Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CustomerProfile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        preferences TEXT,
        total_spent REAL DEFAULT 0,
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
    )
    ''')

    # admins Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # roles Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        permissions TEXT
    )
    ''')

    # promotions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Promotions (
        promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        discount_percentage REAL NOT NULL,
        start_date TIMESTAMP NOT NULL,
        end_date TIMESTAMP NOT NULL,
        tier TEXT,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )
    ''')

    # activity Log Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ActivityLog (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES Admins(admin_id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()