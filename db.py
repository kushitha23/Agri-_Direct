
import sqlite3


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db_connection()

    # USERS TABLE

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fullname TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            phone TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',

            is_blocked INTEGER DEFAULT 0,

            verified INTEGER DEFAULT 0

        )
    """)

    # PRODUCTS TABLE

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
                 farmers_id INTEGER,

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT NOT NULL,

            price REAL NOT NULL,

            stock INTEGER NOT NULL,

            description TEXT,

            image TEXT

        )
    """)

    # ORDERS TABLE

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            buyer_id INTEGER,

            product_name TEXT NOT NULL,

            quantity INTEGER NOT NULL,

            total_price REAL NOT NULL,

            payment_method TEXT NOT NULL,

            status TEXT DEFAULT 'Paid',

            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS buyer_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            fullname TEXT,
            phone TEXT,
            address TEXT
        )
    """)
    conn.execute("""
CREATE TABLE IF NOT EXISTS wishlist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER,
    product_id INTEGER
)
""")
    
    conn.execute("""

CREATE TABLE IF NOT EXISTS farmer_payment_details(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    farmer_id INTEGER UNIQUE,

    upi_id TEXT,

    account_holder TEXT,

    account_number TEXT,

    ifsc_code TEXT

)

""")
    conn.execute("""

DROP TABLE IF EXISTS addresses;

""")

    conn.execute("""

CREATE TABLE addresses(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    address_name TEXT NOT NULL,

    address_line1 TEXT NOT NULL,

    address_line2 TEXT,

    city TEXT NOT NULL,

    state TEXT NOT NULL,

    pincode TEXT NOT NULL,

    FOREIGN KEY(user_id)
    REFERENCES users(id)

);

""")
    # NOTIFICATIONS TABLE

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            message TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ACTIVITY LOGS TABLE

    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            action TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    # CHECK IF PRODUCTS ALREADY EXIST

    existing_products = conn.execute(
        "SELECT COUNT(*) as total FROM products"
    ).fetchone()["total"]

    if existing_products == 0:

        products = [

            (
                "Organic Tomatoes",
                "Vegetables",
                40,
                100,
                "Fresh farm tomatoes directly from farmers.",
                "https://images.unsplash.com/photo-1546094096-0df4bcaaa337"
            ),

            (
                "Sweet Mangoes",
                "Fruits",
                120,
                100,
                "Juicy Alphonso mangoes from orchards.",
                "https://images.unsplash.com/photo-1553279768-865429fa0078"
            ),

            (
                "Basmati Rice",
                "Grains",
                90,
                100,
                "Premium aromatic basmati rice.",
                "https://images.unsplash.com/photo-1586201375761-83865001e31c"
            ),

            (
                "Fresh Vegetables",
                "Vegetables",
                35,
                100,
                "Natural farm vegetables with freshness.",
                "https://images.unsplash.com/photo-1518843875459-f738682238a6"
            ),

            (
                "Fresh Milk",
                "Dairy",
                60,
                100,
                "Pure organic milk from farms.",
                "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=800"
            ),

            (
                "Organic Carrots",
                "Vegetables",
                50,
                100,
                "Healthy carrots full of nutrients.",
                "https://images.unsplash.com/photo-1445282768818-728615cc910a"
            ),

            (
                "Fresh Apples",
                "Fruits",
                140,
                100,
                "Crispy red apples directly from farms.",
                "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce"
            ),

            (
                "Fresh Fruits",
                "Fruits",
                30,
                100,
                "Farm fresh fruits with premium quality.",
                "https://images.unsplash.com/photo-1610832958506-aa56368176cf"
            )

        ]

        conn.executemany(
            """
            INSERT INTO products
            (name, category, price, stock, description, image)

            VALUES (?, ?, ?, ?, ?, ?)
            """,
            products
        )

        conn.commit()

    conn.close()


create_tables()

