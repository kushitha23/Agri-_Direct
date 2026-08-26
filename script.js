/* =========================================
   AGRI-DIRECT COMPLETE COMMON SCRIPT
========================================= */

/* =========================================
   LOCAL STORAGE
========================================= */

let cart = JSON.parse(
localStorage.getItem("cart")
) || [];

let products = JSON.parse(
localStorage.getItem("products")
) || [];

let orders = JSON.parse(
localStorage.getItem("orders")
) || [];

/* =========================================
   MOBILE MENU
========================================= */

function toggleMenu(){

    let nav =
    document.getElementById(
    "navLinks"
    );

    nav.classList.toggle(
    "active"
    );
}

/* =========================================
   ADD TO CART
========================================= */

function addToCart(
event,
name,
price,
image
){

    let product = {

        name:name,

        price:price,

        image:image,

        quantity:1
    };

    let existingProduct =
    cart.find(item =>
    item.name === name
    );

    if(existingProduct){

        existingProduct.quantity++;
    }

    else{

        cart.push(product);
    }

    localStorage.setItem(
    "cart",
    JSON.stringify(cart)
    );

    updateCartCount();

    showToast(
    name +
    " added to cart"
    );
}

/* =========================================
   UPDATE CART COUNT
========================================= */

function updateCartCount(){

    let count =
    document.getElementById(
    "cartCount"
    );

    if(count){

        count.innerText =
        cart.length;
    }
}

/* =========================================
   LOAD CART ITEMS
========================================= */

function loadCartItems(){

    let cartContainer =
    document.getElementById(
    "cartItems"
    );

    let total =
    document.getElementById(
    "cartTotal"
    );

    if(!cartContainer) return;

    cartContainer.innerHTML = "";

    let totalAmount = 0;

    cart.forEach((item,index)=>{

        totalAmount +=
        item.price *
        item.quantity;

        cartContainer.innerHTML += `

        <div class="cart-card">

            <img src="${item.image}">

            <div>

                <h3>${item.name}</h3>

                <p>₹${item.price}</p>

                <p>
                Quantity:
                ${item.quantity}
                </p>

                <button
                onclick="removeCartItem(${index})">

                    Remove

                </button>

            </div>

        </div>

        `;
    });

    if(total){

        total.innerText =
        "₹" +
        totalAmount;
    }
}

/* =========================================
   REMOVE CART ITEM
========================================= */

function removeCartItem(index){

    cart.splice(index,1);

    localStorage.setItem(
    "cart",
    JSON.stringify(cart)
    );

    loadCartItems();

    updateCartCount();

    showToast(
    "Item Removed"
    );
}

/* =========================================
   SEARCH PRODUCTS
========================================= */

function searchProducts(){

    let input =
    document.getElementById(
    "searchInput"
    ).value.toLowerCase();

    let products =
    document.querySelectorAll(
    ".product-card"
    );

    products.forEach(product=>{

        let text =
        product.innerText
        .toLowerCase();

        if(text.includes(input)){

            product.style.display =
            "block";
        }

        else{

            product.style.display =
            "none";
        }
    });
}

/* =========================================
   TOAST NOTIFICATION
========================================= */

function showToast(message){

    let toast =
    document.createElement(
    "div"
    );

    toast.className =
    "toast";

    toast.innerText =
    message;

    document.body.appendChild(
    toast
    );

    setTimeout(()=>{

        toast.classList.add(
        "show"
        );

    },100);

    setTimeout(()=>{

        toast.remove();

    },3000);
}

/* =========================================
   DARK MODE
========================================= */

function toggleDarkMode(){

    document.body.classList.toggle(
    "dark-mode"
    );
}

/* =========================================
   SAVE PRODUCT
========================================= */

function saveProduct(product){

    products.push(product);

    localStorage.setItem(
    "products",
    JSON.stringify(products)
    );

    showToast(
    "Product Added Successfully"
    );
}

/* =========================================
   LOAD PRODUCTS
========================================= */

function loadProducts(){

    let container =
    document.getElementById(
    "productsContainer"
    );

    if(!container) return;

    container.innerHTML = "";

    products.forEach(product=>{

        container.innerHTML += `

        <div class="product-card">

            <img src="${product.image}">

            <div class="product-content">

                <span class="category">

                    ${product.category}

                </span>

                <h3>${product.name}</h3>

                <p>${product.description}</p>

                <div class="product-bottom">

                    <div class="price">

                        ₹${product.price}

                    </div>

                </div>

                <button class="buy-btn"

                onclick="addToCart(
                event,
                '${product.name}',
                ${product.price},
                '${product.image}'
                )">

                    Add To Cart

                </button>

            </div>

        </div>

        `;
    });
}

/* =========================================
   PLACE ORDER
========================================= */

function placeOrder(){

    let order = {

        id:
        "AGR" +
        Math.floor(
        Math.random() * 10000
        ),

        items:cart,

        date:
        new Date()
        .toLocaleDateString(),

        status:"Pending"
    };

    orders.push(order);

    localStorage.setItem(
    "orders",
    JSON.stringify(orders)
    );

    cart = [];

    localStorage.setItem(
    "cart",
    JSON.stringify(cart)
    );

    showToast(
    "Order Placed Successfully"
    );

    setTimeout(()=>{

        window.location.href =
        "order-success.html";

    },1500);
}

/* =========================================
   LOAD ORDER HISTORY
========================================= */

function loadOrders(){

    let container =
    document.getElementById(
    "ordersContainer"
    );

    if(!container) return;

    container.innerHTML = "";

    orders.forEach(order=>{

        container.innerHTML += `

        <div class="order-card">

            <h3>
            Order ID:
            ${order.id}
            </h3>

            <p>
            Date:
            ${order.date}
            </p>

            <p>
            Status:
            ${order.status}
            </p>

        </div>

        `;
    });
}

/* =========================================
   LOGIN SYSTEM
========================================= */

function loginUser(){

    let email =
    document.getElementById(
    "email"
    ).value;

    let password =
    document.getElementById(
    "password"
    ).value;

    /* CUSTOMER */

    if(
    email === "customer@gmail.com"
    &&
    password === "123456"
    ){

        showToast(
        "Customer Login Success"
        );

        setTimeout(()=>{

            window.location.href =
            "index.html";

        },1000);
    }

    /* FARMER */

    else if(
    email === "farmer@gmail.com"
    &&
    password === "123456"
    ){

        showToast(
        "Farmer Login Success"
        );

        setTimeout(()=>{

            window.location.href =
            "farmer-dashboard.html";

        },1000);
    }

    /* ADMIN */

    else if(
    email === "admin@gmail.com"
    &&
    password === "admin123"
    ){

        showToast(
        "Admin Login Success"
        );

        setTimeout(()=>{

            window.location.href =
            "admin-dashboard.html";

        },1000);
    }

    else{

        showToast(
        "Invalid Email or Password"
        );
    }
}

/* =========================================
   PAGE LOADER
========================================= */

window.onload = function(){

    let loader =
    document.getElementById(
    "loader"
    );

    if(loader){

        loader.style.display =
        "none";
    }

    updateCartCount();

    loadCartItems();

    loadProducts();

    loadOrders();
};
function toggleDarkMode(){

    document.body.classList.toggle(
    "dark-mode"
    );

    localStorage.setItem(

        "darkMode",

        document.body.classList.contains(
        "dark-mode"
        )
    );
}

/* LOAD DARK MODE */

window.onload = function(){

    let darkMode =
    localStorage.getItem(
    "darkMode"
    );

    if(darkMode === "true"){

        document.body.classList.add(
        "dark-mode"
        );
    }
};