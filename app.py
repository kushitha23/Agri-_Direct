import email
from fileinput import filename

from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
import razorpay
import json
import re
MARKET_PRICES = {

    "Organic Tomatoes": 45,

    "Sweet Mangoes": 110,

    "Basmati Rice": 95,

    "Fresh Apples": 150,

    "Fresh Milk": 65,

    "Organic Carrots": 55,

    "Green Chillies": 20,

    "Fresh Vegetables": 40

}

app = Flask(__name__)

app.secret_key = "secret"
import razorpay

RAZORPAY_KEY_ID = "rzp_test_SvF91JWczZnF6v"
RAZORPAY_KEY_SECRET = "v3ey6Vo7k43b7fPAjVwYVwiQ"

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)
@app.route("/create-razorpay-order", methods=["POST"])
def create_razorpay_order():

    amount = int(float(request.form["amount"]) * 100)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return {
        "order_id": order["id"],
        "key": RAZORPAY_KEY_ID
    }

# ================= HOME =================

@app.route("/")
def home():
    return render_template("register.html")



@app.route("/index.html")
def index():
    return render_template("index.html")


# ================= AUTH =================

@app.route("/login.html", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE phone = ? AND password = ?
            """,
            (phone, password)
        ).fetchone()

        conn.close()

        if user:

            # CHECK IF USER IS BLOCKED

            if user["is_blocked"] == 1:

                flash(
                    "Your account has been blocked by Admin!",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            # GENERATE OTP

            import random

            otp = str(
                random.randint(100000, 999999)
            )

            # STORE OTP IN SESSION

            session["otp"] = otp

            # STORE USER DETAILS TEMPORARILY

            session["temp_user_id"] = user["id"]

            session["temp_role"] = user["role"]

            session["temp_name"] = user["fullname"]

            print("OTP:", otp)

            flash(
                f"Your OTP is {otp}",
                "success"
            )

            return redirect(
                url_for("verify_otp")
            )

        flash(
            "Invalid Phone or Password!",
            "error"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        entered_otp = request.form["otp"]

        # Check OTP

        if entered_otp == session.get("otp"):

            # OTP correct

            session["user_id"] = session["temp_user_id"]

            session["role"] = session["temp_role"]

            session["name"] = session["temp_name"]

            # Remove temporary data

            session.pop("otp", None)

            session.pop("temp_user_id", None)

            session.pop("temp_role", None)

            session.pop("temp_name", None)

            # Redirect based on role

            if session["role"] == "buyer":

                return redirect(
                    url_for("index")
                )

            elif session["role"] == "farmer":

                return redirect(
                    url_for("farmerDashboard")
                )

            elif session["role"] == "admin":

                return redirect(
                    url_for("adminDashboard")
                )

        else:

            flash(
                "Invalid OTP!",
                "error"
            )

            return redirect(
                url_for("verify_otp")
            )

    return render_template(
        "verify_otp.html"
    )



import re

@app.route("/register.html", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"].strip()
        email = request.form.get("email", "").strip()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]
        role = request.form["role"]

        # NAME VALIDATION

        if not re.match(r'^[A-Za-z ]+$', fullname):
            flash(
                "Name should contain only letters and spaces!",
                "error"
            )
            return render_template("register.html")

        # PHONE VALIDATION

        if not re.match(r'^[6-9]\d{9}$', phone):
            flash(
                "Enter a valid Indian phone number!",
                "error"
            )
            return render_template("register.html")

        # EMAIL REQUIRED FOR BUYERS

        if role == "buyer" and not email:
            flash(
                "Email is required for buyers!",
                "error"
            )
            return render_template("register.html")

        # PASSWORD REQUIRED

        if not password:
            flash(
                "Password is required!",
                "error"
            )
            return render_template("register.html")

        # CONFIRM PASSWORD REQUIRED

        if not confirmPassword:
            flash(
                "Please confirm your password!",
                "error"
            )
            return render_template("register.html")

        # EMAIL VALIDATION

        if email:

            if not re.match(
                r'^[A-Za-z0-9._%+-]+@(gmail\.com|yahoo\.com)$',
                email,
                re.IGNORECASE
            ):
                flash(
                    "Only Gmail or Yahoo email addresses are allowed!",
                    "error"
                )
                return render_template("register.html")

        # PASSWORD MATCH CHECK

        if password != confirmPassword:

            flash(
                "Passwords do not match!",
                "error"
            )

            return render_template("register.html")

        # PASSWORD LENGTH CHECK

        if len(password) < 6:

            flash(
                "Password must contain minimum 6 characters!",
                "error"
            )

            return render_template("register.html")

        # WEAK PASSWORD CHECK

        weak_passwords = [
            "123456",
            "abcdef",
            "qwerty",
            "password"
        ]

        if password.lower() in weak_passwords:

            flash(
                "Choose a stronger password!",
                "error"
            )

            return render_template("register.html")

        conn = get_db_connection()

        # DUPLICATE PHONE CHECK

        existing_phone = conn.execute(
            """
            SELECT * FROM users
            WHERE phone = ?
            """,
            (phone,)
        ).fetchone()

        if existing_phone:

            flash(
                "Phone number already exists!",
                "error"
            )

            conn.close()

            return render_template("register.html")

        # DUPLICATE EMAIL CHECK

        if email:

            existing_email = conn.execute(
                """
                SELECT * FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            if existing_email:

                flash(
                    "Email already exists!",
                    "error"
                )

                conn.close()

                return render_template("register.html")

        # INSERT USER

        conn.execute(
            """
            INSERT INTO users
            (fullname, email, phone, password, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                fullname,
                email,
                phone,
                password,
                role
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Registration Successful!",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/create-admin")
def createAdmin():

    conn = get_db_connection()

    admin = conn.execute(
        """
        SELECT *
        FROM users
        WHERE role='admin'
        """
    ).fetchone()

    if not admin:

        conn.execute(
            """
            INSERT INTO users
            (
                fullname,
                email,
                phone,
                password,
                role,
                status,
                is_blocked,
                verified
            )

            VALUES
            (
                'Admin',
                'admin@agridirect.com',
                '9999999999',
                'admin123',
                'admin',
                'Approved',
                0,
                1
            )
            """
        )

        conn.commit()

    conn.close()

    return "Admin Created Successfully"


# ================= MAIN PAGES =================

@app.route("/about.html")
def about():
    return render_template("about.html")


@app.route("/contact.html")
def contact():
    return render_template("contact.html")


@app.route("/products.html")
def products():

    conn = get_db_connection()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "products.html",
        products=products
    )


@app.route("/cart.html")
def cart():
    return render_template("cart.html")

@app.route("/checkout.html")
def checkout():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    addresses = conn.execute(
        """
        SELECT *
        FROM addresses

        WHERE user_id = ?

        ORDER BY id DESC
        """,

        (

            session["user_id"],

        )

    ).fetchall()

    conn.close()

    return render_template(

        "checkout.html",

        addresses=addresses

    )

@app.route("/order-success.html")
def orderSuccess():
    return render_template("order-success.html")

@app.route("/reject-order/<int:order_id>")
def rejectOrder(order_id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE orders SET status=? WHERE id=?",
        ("Rejected", order_id)
    )

    conn.commit()

    return redirect("/farmer-orders.html")

@app.route("/farmer-orders.html")
def farmerOrders():

    farmer_id = session["user_id"]

    conn = get_db_connection()

    orders = conn.execute(
        """
        SELECT
    orders.*,
    users.fullname as buyer_name

FROM orders

LEFT JOIN users
ON orders.buyer_id = users.id

WHERE orders.farmer_id = ?

ORDER BY orders.id DESC
        """,
        (farmer_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "farmer-orders.html",
        orders=orders
    )

@app.route("/order-history.html")
def orderHistory():
    return render_template("order-history.html")


# ================= PRODUCT DETAILS =================

@app.route("/apple-details.html")
def appleDetails():
    return render_template("apple-details.html")


@app.route("/carrot-details.html")
def carrotDetails():
    return render_template("carrot-details.html")


@app.route("/fruits-details.html")
def fruitsDetails():
    return render_template("fruits-details.html")


@app.route("/mango-details.html")
def mangoDetails():
    return render_template("mango-details.html")


@app.route("/milk-details.html")
def milkDetails():
    return render_template("milk-details.html")


@app.route("/rice-details.html")
def riceDetails():
    return render_template("rice-details.html")


@app.route("/tomato-details.html")
def tomatoDetails():
    return render_template("tomato-details.html")


@app.route("/vegetables-details.html")
def vegetablesDetails():
    return render_template("vegetables-details.html")



@app.route("/product/<int:product_id>")
def productDetails(product_id):

    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT
            products.*,
            users.fullname as farmer_name,
            users.email as farmer_email,
            users.phone as farmer_phone

        FROM products

        LEFT JOIN users
        ON products.farmer_id = users.id

        WHERE products.id = ?
        """,
        (product_id,)
    ).fetchone()

    conn.close()

    if product is None:
        return "Product Not Found"

    return render_template(
        "product-details.html",
        product=product
    )
@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    addresses = conn.execute(
        """
        SELECT *
        FROM addresses
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(

        "profile.html",

        user=user,

        addresses=addresses

    )
@app.route("/add_address", methods=["GET", "POST"])
def add_address():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    # Check address count

    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM addresses
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    if request.method == "POST":

        if count >= 5:

            flash(
                "You can add a maximum of 5 addresses.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("profile")
            )

        address_name = request.form["address_name"]

        address_line1 = request.form["address_line1"]

        address_line2 = request.form["address_line2"]

        city = request.form["city"]

        state = request.form["state"]

        pincode = request.form["pincode"]

        conn.execute(
            """
            INSERT INTO addresses(

                user_id,

                address_name,

                address_line1,

                address_line2,

                city,

                state,

                pincode

            )

            VALUES(?,?,?,?,?,?,?)
            """,

            (

                session["user_id"],

                address_name,

                address_line1,

                address_line2,

                city,

                state,

                pincode

            )

        )

        conn.commit()

        conn.close()

        flash(
            "Address added successfully!",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    conn.close()

    return render_template(
        "add_address.html"
    )
@app.route("/delete_address/<int:id>")
def delete_address(id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM addresses

        WHERE id = ?

        AND user_id = ?
        """,

        (

            id,

            session["user_id"]

        )

    )

    conn.commit()

    conn.close()

    flash(

        "Address deleted successfully!",

        "success"

    )

    return redirect(

        url_for("profile")

    )
@app.route("/edit_address/<int:id>", methods=["GET", "POST"])
def edit_address(id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    address = conn.execute(
        """
        SELECT *
        FROM addresses

        WHERE id = ?

        AND user_id = ?
        """,

        (

            id,

            session["user_id"]

        )

    ).fetchone()

    if not address:

        conn.close()

        flash(
            "Address not found!",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    if request.method == "POST":

        conn.execute(
            """

            UPDATE addresses

            SET

            address_name = ?,

            address_line1 = ?,

            address_line2 = ?,

            city = ?,

            state = ?,

            pincode = ?

            WHERE id = ?

            AND user_id = ?

            """,

            (

                request.form["address_name"],

                request.form["address_line1"],

                request.form["address_line2"],

                request.form["city"],

                request.form["state"],

                request.form["pincode"],

                id,

                session["user_id"]

            )

        )

        conn.commit()

        conn.close()

        flash(
            "Address updated successfully!",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    conn.close()

    return render_template(
        "edit_address.html",

        address=address

    )
# ================= FARMER =================
@app.route("/mandi-prices")
def mandiPrices():

    mandi_prices = [

        {

            "commodity":"Tomato",

            "market":"Madanapalle",

            "district":"Annamayya",

            "price":"₹1500"

        },

        {

            "commodity":"Mango",

            "market":"Chittoor",

            "district":"Chittoor",

            "price":"₹3000"

        },

        {

            "commodity":"Onion",

            "market":"Tirupati",

            "district":"Tirupati",

            "price":"₹2200"

        },

        {

            "commodity":"Groundnut",

            "market":"Anantapur",

            "district":"Anantapur",

            "price":"₹5500"

        }

    ]

    return render_template(

        "mandi-prices.html",

        mandi_prices=mandi_prices

    )

@app.route("/farmer-dashboard.html")
def farmerDashboard():

    import random

    farmer_id = session["user_id"]

    conn = get_db_connection()

    # Total Products

    total_products = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM products
        WHERE farmer_id = ?
        """,

        (farmer_id,)

    ).fetchone()["total"]


    # Total Orders

    total_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        WHERE farmer_id = ?
        """,

        (farmer_id,)

    ).fetchone()["total"]


    # Total Revenue

    total_revenue = conn.execute(
        """
        SELECT COALESCE(
            SUM(total_price),
            0
        ) as revenue

        FROM orders

        WHERE farmer_id = ?

        AND status IN
        (

            'Delivered',

            'Completed'

        )
        """,

        (farmer_id,)

    ).fetchone()["revenue"]


    # Pending Orders

    pending_orders = conn.execute(
        """
        SELECT COUNT(*) as total

        FROM orders

        WHERE farmer_id = ?

        AND status IN
        (

            'Paid',

            'Accepted',

            'Shipped'

        )
        """,

        (farmer_id,)

    ).fetchone()["total"]


    # Today's Orders

    today_orders = conn.execute(
        """
        SELECT COUNT(*) as total

        FROM orders

        WHERE farmer_id = ?

        AND date(order_date)=date('now')
        """,

        (farmer_id,)

    ).fetchone()["total"]


    # Today's Revenue

    today_revenue = conn.execute(
        """
        SELECT COALESCE(
            SUM(total_price),
            0
        ) as revenue

        FROM orders

        WHERE farmer_id = ?

        AND status IN
        (

            'Delivered',

            'Completed'

        )

        AND date(order_date)=date('now')
        """,

        (farmer_id,)

    ).fetchone()["revenue"]


    # Best Selling Product

    best_product = conn.execute(
        """
        SELECT

            product_name,

            COUNT(*) as total_sales

        FROM orders

        WHERE farmer_id = ?

        GROUP BY product_name

        ORDER BY total_sales DESC

        LIMIT 1
        """,

        (farmer_id,)

    ).fetchone()


    # Payment Details

    payment = conn.execute(
        """

        SELECT *

        FROM farmer_payment_details

        WHERE farmer_id = ?

        """,

        (

            farmer_id,

        )

    ).fetchone()


    # Notifications

    new_orders = conn.execute(
        """

        SELECT COUNT(*) as total

        FROM orders

        WHERE farmer_id = ?

        AND status='Paid'

        """,

        (

            farmer_id,

        )

    ).fetchone()["total"]


    pending_deliveries = conn.execute(
        """

        SELECT COUNT(*) as total

        FROM orders

        WHERE farmer_id = ?

        AND status IN

        (

            'Accepted',

            'Shipped'

        )

        """,

        (

            farmer_id,

        )

    ).fetchone()["total"]


    # Revenue Growth

    growth_percent = 25


    # Farming Tips

    tips = [

        "💧 Water crops early morning to reduce evaporation.",

        "🌱 Use organic compost for healthier soil.",

        "🐞 Encourage beneficial insects for natural pest control.",

        "☀️ Check weather forecasts before irrigation.",

        "🚜 Rotate crops regularly to improve soil fertility."

    ]

    daily_tip = random.choice(tips)


    conn.close()


    return render_template(

        "farmer-dashboard.html",

        total_products=total_products,

        total_orders=total_orders,

        total_revenue=total_revenue,

        pending_orders=pending_orders,

        today_orders=today_orders,

        today_revenue=today_revenue,

        best_product=best_product,

        growth_percent=growth_percent,

        daily_tip=daily_tip,

        payment=payment,

        new_orders=new_orders,

        pending_deliveries=pending_deliveries

    )
@app.route("/update-product/<int:product_id>", methods=["POST"])
def updateProduct(product_id):

    name = request.form["name"]
    category = request.form["category"]
    price = request.form["price"]
    stock = request.form["stock"]

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE products
        SET
        name=?,
        category=?,
        price=?,
        stock=?
        WHERE id=?
        """,
        (
            name,
            category,
            price,
            stock,
            product_id
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("farmerProducts"))

     
@app.route("/update-order-status/<int:order_id>/<status>")
def updateOrderStatus(order_id, status):

    conn = get_db_connection()

    if status == "Rejected":

        order = conn.execute(
            """
            SELECT payment_method
            FROM orders
            WHERE id = ?
            """,
            (order_id,)
        ).fetchone()

        if order:

            if order["payment_method"].lower() == "razorpay":

                status = "Refund Requested"

            else:

                status = "Rejected"

    conn.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """,
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect("/farmer-orders.html")
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('.', filename)
import os
from werkzeug.utils import secure_filename

from flask import request, render_template, redirect, url_for, flash, session
import base64

@app.route("/add-product.html", methods=["GET", "POST"])
def addProduct():

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"]

        image = request.files["image"]

        image_data = base64.b64encode(
            image.read()
        ).decode("utf-8")

        farmer_id = session.get("user_id")

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO products
            (
                name,
                category,
                price,
                stock,
                description,
                image,
                farmer_id
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                category,
                price,
                stock,
                description,
                image_data,
                farmer_id
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Product Added Successfully!",
            "success"
        )

        return redirect(
            url_for("farmerProducts")
        )

    return render_template(
        "add-product.html"
    )
@app.route("/farmer-products.html")
def farmerProducts():

    if "user_id" not in session:
        return redirect(url_for("login"))

    farmer_id = session["user_id"]

    conn = get_db_connection()

    products = conn.execute(
        """
        SELECT *
        FROM products
        WHERE farmer_id = ?
        ORDER BY id DESC
        """,
        (farmer_id,)
    ).fetchall()

    total_products = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM products
        WHERE farmer_id = ?
        """,
        (farmer_id,)
    ).fetchone()["total"]

    out_of_stock = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM products
        WHERE farmer_id = ?
        AND stock = 0
        """,
        (farmer_id,)
    ).fetchone()["total"]

    available_products = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM products
        WHERE farmer_id = ?
        AND stock > 0
        """,
        (farmer_id,)
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "farmer-products.html",
        products=products,
        total_products=total_products,
        out_of_stock=out_of_stock,
        available_products=available_products
    )
@app.route("/show-products")
def showProducts():

    conn = get_db_connection()

    products = conn.execute(
        """
        SELECT id, name, farmer_id
        FROM products
        """
    ).fetchall()

    conn.close()

    return str([dict(product) for product in products])
@app.route("/show-farmers")
def showFarmers():

    conn = get_db_connection()

    farmers = conn.execute(
        """
        SELECT id, fullname, email
        FROM users
        WHERE role='farmer'
        """
    ).fetchall()

    conn.close()

    return str([dict(farmer) for farmer in farmers])
import json

@app.route("/save-order", methods=["POST"])
def saveOrder():

    buyer_id = session.get("user_id")

    if not buyer_id:

        return "Please Login"

    payment_method = request.form["payment_method"]

    if payment_method == "cod":

        status = "Pending Payment"

    else:

        status = "Paid"

    cart = json.loads(

        request.form["cart"]

    )

    conn = get_db_connection()

    for item in cart:

        conn.execute(

            """

            INSERT INTO orders

            (

                buyer_id,

                product_name,

                quantity,

                total_price,

                payment_method,

                status

            )

            VALUES

            (

                ?,

                ?,

                ?,

                ?,

                ?,

                ?

            )

            """,

            (

                buyer_id,

                item["name"],

                item["quantity"],

                float(item["price"]) * int(item["quantity"]),

                payment_method,

                status

            )

        )

    conn.commit()

    conn.close()

    return "Order Saved Successfully"
@app.route(
    "/save-payment-details",

    methods=["POST"]
)

def save_payment_details():

    farmer_id = session["user_id"]

    upi_id = request.form["upi_id"]

    account_holder = request.form["account_holder"]

    account_number = request.form["account_number"]

    ifsc_code = request.form["ifsc_code"]

    conn = get_db_connection()

    existing = conn.execute(

        """

        SELECT *

        FROM farmer_payment_details

        WHERE farmer_id = ?

        """,

        (

            farmer_id,

        )

    ).fetchone()

    if existing:

        conn.execute(

            """

            UPDATE farmer_payment_details

            SET

            upi_id=?,

            account_holder=?,

            account_number=?,

            ifsc_code=?

            WHERE farmer_id=?

            """,

            (

                upi_id,

                account_holder,

                account_number,

                ifsc_code,

                farmer_id

            )

        )

    else:

        conn.execute(

            """

            INSERT INTO

            farmer_payment_details

            (

                farmer_id,

                upi_id,

                account_holder,

                account_number,

                ifsc_code

            )

            VALUES

            (

                ?, ?, ?, ?, ?

            )

            """,

            (

                farmer_id,

                upi_id,

                account_holder,

                account_number,

                ifsc_code

            )

        )

    conn.commit()

    conn.close()

    flash(

        "Payment details saved successfully!",

        "success"

    )

    return redirect(

        url_for("farmerDashboard")

    )
    
@app.route("/my-orders")
def myOrders():

    buyer_id = session.get("user_id")

    if not buyer_id:
        return redirect(url_for("login"))

    conn = get_db_connection()

    orders = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE buyer_id = ?
        ORDER BY id DESC
        """,
        (buyer_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "my-orders.html",
        orders=orders
    )
@app.route("/track-order/<int:order_id>")
def trackOrder(order_id):

    conn = get_db_connection()

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "order-tracking.html",
        order=order
    )

@app.route("/check-session")
def checkSession():

    return str({
        "user_id": session.get("user_id"),
        "name": session.get("name"),
        "role": session.get("role")
    })
@app.route("/confirm-receipt/<int:order_id>")
def confirmReceipt(order_id):

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE orders
        SET status = 'Completed'
        WHERE id = ?
        """,
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/my-orders")
@app.route("/ship-order/<int:order_id>", methods=["GET", "POST"])
def shipOrder(order_id):

    conn = get_db_connection()

    if request.method == "POST":

        estimated_date = request.form["estimated_date"]
        estimated_time = request.form["estimated_time"]

        conn.execute(
            """
            UPDATE orders
            SET
                status='Shipped',
                estimated_date=?,
                estimated_time=?
            WHERE id=?
            """,
            (
                estimated_date,
                estimated_time,
                order_id
            )
        )

        conn.commit()
        conn.close()

        return redirect("/farmer-orders.html")

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE id=?
        """,
        (order_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "ship-order.html",
        order=order
    )
# ================= ADMIN =================

@app.route("/admin-dashboard.html")
def adminDashboard():

    conn = get_db_connection()

    total_farmers = conn.execute(
        "SELECT COUNT(*) as total FROM users WHERE role='farmer'"
    ).fetchone()["total"]

    total_buyers = conn.execute(
        "SELECT COUNT(*) as total FROM users WHERE role='buyer'"
    ).fetchone()["total"]

    total_orders = conn.execute(
        "SELECT COUNT(*) as total FROM orders"
    ).fetchone()["total"]

    total_products = conn.execute(
        "SELECT COUNT(*) as total FROM products"
    ).fetchone()["total"]

    revenue = conn.execute(
        """
        SELECT COALESCE(SUM(total_price),0) as revenue
        FROM orders
        WHERE status='Delivered'
        """
    ).fetchone()

    total_revenue = revenue["revenue"]
    recent_farmers = conn.execute(
    """
    SELECT *
    FROM users
    WHERE role='farmer'
    ORDER BY id DESC
    LIMIT 5
    """
).fetchall()

    conn.close()

    return render_template(
    "admin-dashboard.html",
    total_farmers=total_farmers,
    total_buyers=total_buyers,
    total_orders=total_orders,
    total_products=total_products,
    total_revenue=total_revenue,
    recent_farmers=recent_farmers
)


@app.route("/global-marketplace.html")
def globalMarketplace():

    conn = get_db_connection()

    products = conn.execute(
        """
        SELECT *
        FROM products
        ORDER BY name
        """
    ).fetchall()

    market_data = []

    for product in products:

        market_price = MARKET_PRICES.get(
            product["name"],
            product["price"]
        )

        market_data.append({

            "name": product["name"],

            "your_price": product["price"],
            "category": product["category"],

            "market_price": market_price

        })

    conn.close()

    return render_template(
        "global-marketplace.html",
        products=market_data
    )
@app.route("/manage-buyers.html")
def manageBuyers():

    conn = get_db_connection()

    buyers = conn.execute(
        """
        SELECT *
        FROM users
        WHERE role='buyer'
        ORDER BY id DESC
        """
    ).fetchall()

    total_buyers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='buyer'
        """
    ).fetchone()["total"]

    blocked_buyers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='buyer'
        AND is_blocked = 1
        """
    ).fetchone()["total"]

    active_buyers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='buyer'
        AND is_blocked = 0
        """
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "manage-buyers.html",
        buyers=buyers,
        total_buyers=total_buyers,
        blocked_buyers=blocked_buyers,
        active_buyers=active_buyers
    )





@app.route("/manage-farmers.html")
def manageFarmers():

    conn = get_db_connection()

    farmers = conn.execute(
        """
        SELECT *
        FROM users
        WHERE role='farmer'
        """
    ).fetchall()

    total_farmers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='farmer'
        """
    ).fetchone()["total"]

    approved_farmers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='farmer'
        AND status='Approved'
        """
    ).fetchone()["total"]

    pending_farmers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='farmer'
        AND status='Pending'
        """
    ).fetchone()["total"]

    rejected_farmers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='farmer'
        AND status='Rejected'
        """
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "manage-farmers.html",
        farmers=farmers,
        total_farmers=total_farmers,
        approved_farmers=approved_farmers,
        pending_farmers=pending_farmers,
        rejected_farmers=rejected_farmers
    )



@app.route("/manage-orders.html")
def manageOrders():

    conn = get_db_connection()

    orders = conn.execute(
        """
        SELECT *
        FROM orders
        ORDER BY id DESC
        """
    ).fetchall()

    total_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        """
    ).fetchone()["total"]

    pending_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        WHERE status != 'Delivered'
        AND status != 'Rejected'
        
        """
    ).fetchone()["total"]

    delivered_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        WHERE status = 'Delivered'
        """
    ).fetchone()["total"]

    rejected_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        WHERE status = 'Rejected'
        """
    ).fetchone()["total"]

    total_revenue = conn.execute(
        """
        SELECT COALESCE(SUM(total_price),0) as revenue
        FROM orders
        WHERE status = 'Delivered'
        """
    ).fetchone()["revenue"]

    conn.close()

    return render_template(
        "manage-orders.html",
        orders=orders,
        total_orders=total_orders,
        pending_orders=pending_orders,
        delivered_orders=delivered_orders,
        rejected_orders=rejected_orders,
        total_revenue=total_revenue
    )

@app.route("/admin-delete-product/<int:product_id>")
def adminDeleteProduct(product_id):

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/manage-products.html")

@app.route("/delete-product/<int:product_id>")
def deleteProduct(product_id):

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/farmer-products.html")

@app.route("/edit-product/<int:product_id>")
def editProduct(product_id):

    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit-product.html",
        product=product
    )
@app.route("/manage-products.html")
def manageProducts():

    conn = get_db_connection()

    products = conn.execute(
        """
        SELECT *
        FROM products
        ORDER BY id DESC
        """
    ).fetchall()

    total_products = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM products
        """
    ).fetchone()["total"]

    out_of_stock = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM products
        WHERE stock = 0
        """
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "manage-products.html",
        products=products,
        total_products=total_products,
        out_of_stock=out_of_stock
    )




@app.route("/reports.html")
def reports():

    conn = get_db_connection()

    total_revenue = conn.execute(
        """
        SELECT COALESCE(SUM(total_price),0) as revenue
        FROM orders
        WHERE status IN ('Delivered','Completed')
        """
    ).fetchone()["revenue"]

    total_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        """
    ).fetchone()["total"]

    delivered_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        WHERE status IN ('Delivered','Completed')
        """
    ).fetchone()["total"]

    total_farmers = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM users
        WHERE role='farmer'
        """
    ).fetchone()["total"]
    top_products = conn.execute(
    """
    SELECT
        product_name,
        COUNT(*) as orders_count,
        COALESCE(SUM(total_price),0) as revenue
    FROM orders
    GROUP BY product_name
    ORDER BY orders_count DESC
    LIMIT 5
    """
).fetchall()

    conn.close()

    return render_template(
    "reports.html",
    total_revenue=total_revenue,
    total_orders=total_orders,
    delivered_orders=delivered_orders,
    total_farmers=total_farmers,
    top_products=top_products
)
@app.route("/admin-farmer-details/<int:farmer_id>")
def adminFarmerDetails(farmer_id):

    conn = get_db_connection()

    farmer = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (farmer_id,)
    ).fetchone()

    products = conn.execute(
        """
        SELECT *
        FROM products
        WHERE farmer_id = ?
        """,
        (farmer_id,)
    ).fetchall()

    total_revenue = conn.execute(
        """
        SELECT COALESCE(SUM(total_price),0) as revenue
        FROM orders
        WHERE farmer_id = ?
        AND status IN ('Delivered','Completed')
        """,
        (farmer_id,)
       
    ).fetchone()["revenue"]

    total_orders = conn.execute(
        """
        SELECT COUNT(*) as total
        FROM orders
        WHERE farmer_id = ?
        """,
        (farmer_id,)
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "admin-farmer-details.html",
        farmer=farmer,
        products=products,
        total_revenue=total_revenue,
        total_orders=total_orders
    )

from flask import request

@app.route("/block-user/<int:user_id>")
def blockUser(user_id):

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE users
        SET is_blocked = 1
        WHERE id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect(request.referrer)


@app.route("/unblock-user/<int:user_id>")
def unblockUser(user_id):

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE users
        SET is_blocked = 0
        WHERE id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect(request.referrer)




@app.route("/check-users")
def checkUsers():

    conn = get_db_connection()

    users = conn.execute(
        """
        SELECT id,
               fullname,
               email,
               password,
               role
        FROM users
        """
    ).fetchall()

    conn.close()

    return str([dict(user) for user in users])


# ================= ADMIN FARMER MANAGEMENT =================

@app.route("/approve-farmer/<int:user_id>")
def approveFarmer(user_id):

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE users
        SET status='Approved'
        WHERE id=?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()

    flash("Farmer Approved Successfully!", "success")

    return redirect("/manage-farmers.html")


@app.route("/reject-farmer/<int:user_id>")
def rejectFarmer(user_id):

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE users
        SET status='Rejected'
        WHERE id=?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()

    flash("Farmer Rejected!", "error")

    return redirect("/manage-farmers.html")




# ================= CUSTOMER =================

@app.route("/buyer-dashboard.html")
def buyerDashboard():
    return render_template("buyer-dashboard.html")


# ================= RUN APP =================
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully!", "success")

    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(debug=True)