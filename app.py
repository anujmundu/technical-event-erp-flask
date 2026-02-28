from flask import Flask
from extensions import db
from flask import render_template, request, redirect, session, url_for
from models import User, Vendor, Product, Membership, Category, Cart, Order, OrderItem
from auth_utils import login_required, role_required
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'erp_secret_key'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/seed_categories")
def seed_categories():

    if Category.query.count() == 0:
        categories = [
            "Catering",
            "Florist",
            "Decoration",
            "Lighting",
            "Photography",
            "Music & DJ",
            "Venue Booking",
            "Makeup & Styling"
        ]

        for c in categories:
            db.session.add(Category(name=c))

        db.session.commit()

    return "Categories Seeded"

# Authentication Routes
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # ADMIN / USER stored in User table
        if role in ["admin", "user"]:
            user = User.query.filter_by(email=email, password=password, role=role).first()

            if user:
                session["user_id"] = user.id
                session["role"] = role

                if role == "admin":
                    return redirect("/admin/dashboard")
                else:
                    return redirect("/user/dashboard")

        # VENDOR table
        if role == "vendor":
            vendor = Vendor.query.filter_by(email=email, password=password).first()

            if vendor:
                session["user_id"] = vendor.id
                session["role"] = "vendor"
                return redirect("/vendor/dashboard")

    return render_template("auth/login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        new_user = User(
            name=name,
            email=email,
            password=password,
            role="user"
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("auth/signup.html")

# Admin Routes
@app.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    return render_template("admin/dashboard.html")
    
@app.route("/admin/membership", methods=["GET", "POST"])
@login_required
@role_required("admin")
def membership():

    if request.method == "POST":
        duration = request.form["duration"]

        if duration == "6 months":
            end_date = datetime.utcnow() + timedelta(days=180)
        elif duration == "1 year":
            end_date = datetime.utcnow() + timedelta(days=365)
        else:
            end_date = datetime.utcnow() + timedelta(days=730)

        new_membership = Membership(
            duration=duration,
            end_date=end_date
        )

        db.session.add(new_membership)
        db.session.commit()

        # IMPORTANT FIX
        return redirect(url_for("membership"))

    memberships = Membership.query.all()

    return render_template(
        "admin/membership.html",
        memberships=memberships
    )

@app.route("/admin/update_user_membership/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def update_user_membership(user_id):

    user = User.query.get(user_id)

    if not user:
        return redirect(url_for("maintain_user"))

    # membership_id may be empty (no membership selected)
    new_membership = request.form.get("membership_id")
    if new_membership:
        try:
            user.membership_id = int(new_membership)
        except ValueError:
            user.membership_id = None
    else:
        user.membership_id = None

    db.session.commit()

    return redirect(url_for("maintain_user"))

@app.route("/admin/delete_membership/<int:membership_id>")
@login_required
@role_required("admin")
def delete_membership(membership_id):

    membership = Membership.query.get(membership_id)

    if not membership:
        return redirect(url_for("membership"))

    # Prevent deletion if used by users
    linked_user = User.query.filter_by(
        membership_id=membership_id
    ).first()

    if linked_user:
        return render_template("message.html", message="Cannot delete membership assigned to users.", back_url=url_for("membership"))

    db.session.delete(membership)
    db.session.commit()

    return redirect(url_for("membership"))

@app.route("/admin/maintain_user", methods=["GET", "POST"])
@login_required
@role_required("admin")
def maintain_user():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        # membership_id may be omitted or empty; treat as None
        membership_id = request.form.get("membership_id")
        if membership_id:
            try:
                membership_id = int(membership_id)
            except ValueError:
                membership_id = None
        else:
            membership_id = None

        new_user = User(
            name=name,
            email=email,
            password=password,
            role="user",
            membership_id=membership_id
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("maintain_user"))

    users = User.query.all()
    memberships = Membership.query.all()

    return render_template(
        "admin/maintain_user.html",
        users=users,
        memberships=memberships
    )

@app.route("/admin/edit_user/<int:id>", methods=["GET","POST"])
def edit_user(id):
    user = User.query.get_or_404(id)
    memberships = Membership.query.all()

    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.membership_id = request.form.get("membership_id")

        db.session.commit()
        return redirect("/admin/maintain_user")

    return render_template(
        "admin/edit_user.html",
        user=user,
        memberships=memberships
    )

@app.route("/admin/delete_user/<int:user_id>")
@login_required
@role_required("admin")
def delete_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return redirect(url_for("maintain_user"))

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("maintain_user"))

@app.route("/admin/maintain_vendor", methods=["GET", "POST"])
@login_required
@role_required("admin")
def maintain_vendor():
    categories = Category.query.all()
    
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        category = request.form["category"]

        new_vendor = Vendor(
            name=name,
            email=email,
            password=password,
            category=category
        )

        db.session.add(new_vendor)
        db.session.commit()

        return redirect(url_for("maintain_vendor"))

    vendors = Vendor.query.all()

    return render_template(
        "admin/maintain_vendor.html",
        vendors=vendors,
        categories=categories
    )

@app.route("/admin/edit_vendor/<int:vendor_id>", methods=["GET","POST"])
@login_required
@role_required("admin")
def edit_vendor(vendor_id):

    vendor = Vendor.query.get(vendor_id)

    categories = [
        "Catering","Florist","Decoration","Lighting",
        "Photography","Music & DJ","Venue Booking","Makeup & Styling"
    ]
    
    if request.method == "POST":
        vendor.name = request.form["name"]
        vendor.email = request.form["email"]
        vendor.category = request.form["category"]

        db.session.commit()
        return redirect(url_for("maintain_vendor"))

    return render_template(
        "admin/edit_vendor.html",
        vendor=vendor,
        categories=categories
    )


@app.route("/admin/delete_vendor/<int:vendor_id>")
@login_required
@role_required("admin")
def delete_vendor(vendor_id):

    vendor = Vendor.query.get(vendor_id)

    if not vendor:
        return redirect(url_for("maintain_vendor"))

    # ERP safety check:
    # prevent deletion if vendor has products
    vendor_products = Product.query.filter_by(
        vendor_id=vendor_id
    ).first()

    if vendor_products:
        return render_template("message.html", message="Cannot delete vendor with existing products.", back_url=url_for("maintain_vendor"))

    db.session.delete(vendor)
    db.session.commit()

    return redirect(url_for("maintain_vendor"))

# Vendor Routes
@app.route("/vendor/dashboard")
@login_required
@role_required("vendor")
def vendor_dashboard():
    return render_template("vendor/dashboard.html")
    
@app.route("/vendor/add_item", methods=["GET", "POST"])
@login_required
@role_required("vendor")
def add_item():

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        image = request.form["image"]

        new_product = Product(
            vendor_id=session["user_id"],
            name=name,
            price=price,
            image=image
        )

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("add_item"))

    return render_template("vendor/add_item.html")

@app.route("/vendor/items")
@login_required
@role_required("vendor")
def vendor_items():

    items = Product.query.filter_by(
        vendor_id=session["user_id"]
    ).all()

    return render_template(
        "vendor/items.html",
        items=items
    )

@app.route("/vendor/orders")
@login_required
@role_required("vendor")
def vendor_orders():

    vendor_products = Product.query.filter_by(
        vendor_id=session["user_id"]
    ).all()

    product_ids = [p.id for p in vendor_products]

    order_items = OrderItem.query.filter(
        OrderItem.product_id.in_(product_ids)
    ).all()

    order_ids = list(set([oi.order_id for oi in order_items]))

    orders = Order.query.filter(
        Order.id.in_(order_ids)
    ).all()

    return render_template(
        "vendor/orders.html",
        orders=orders
    )

@app.route("/vendor/update_status/<int:order_id>", methods=["POST"])
@login_required
@role_required("vendor")
def update_status(order_id):

    new_status = request.form["status"]

    order = Order.query.get(order_id)

    # Status workflow: Received -> Ready for Shipping -> Out for Delivery
    allowed_flow = [
        "Received",
        "Ready for Shipping",
        "Out for Delivery"
    ]

    if allowed_flow.index(new_status) >= allowed_flow.index(order.status):
        order.status = new_status
        db.session.commit()

    return redirect(url_for("vendor_orders"))

# User Routes
@app.route("/user/dashboard")
@login_required
@role_required("user")
def user_dashboard():
    return render_template("user/dashboard.html")

@app.route("/user/vendors")
@login_required
@role_required("user")
def user_vendors():

    category = request.args.get("category")

    categories = Category.query.all()

    if category:
        vendors = Vendor.query.filter_by(category=category).all()
    else:
        vendors = []

    return render_template(
        "user/vendors.html",
        vendors=vendors,
        categories=categories
    )

@app.route("/user/products/<int:vendor_id>")
@login_required
@role_required("user")
def user_products(vendor_id):

    products = Product.query.filter_by(vendor_id=vendor_id).all()

    return render_template(
        "user/products.html",
        products=products
    )

@app.route("/user/add_to_cart", methods=["POST"])
@login_required
@role_required("user")
def add_to_cart():

    product_id = request.form["product_id"]

    existing = Cart.query.filter_by(
        user_id=session["user_id"],
        product_id=product_id
    ).first()

    if existing:
        existing.quantity += 1
    else:
        new_item = Cart(
            user_id=session["user_id"],
            product_id=product_id,
            quantity=1
        )
        db.session.add(new_item)

    db.session.commit()

    # Redirect back to same page (PRG pattern preserved)
    return redirect(request.referrer or url_for("user_dashboard"))

@app.route("/user/cart")
@login_required
@role_required("user")
def view_cart():

    cart_items = Cart.query.filter_by(
        user_id=session["user_id"]
    ).all()

    items = []
    grand_total = 0

    for cart in cart_items:
        product = Product.query.get(cart.product_id)

        items.append({
            "id": cart.id,
            "quantity": cart.quantity,
            "product": product
        })

        grand_total += product.price * cart.quantity

    return render_template(
        "user/cart.html",
        items=items,
        grand_total=grand_total
    )

@app.route("/user/increase/<int:cart_id>")
@login_required
@role_required("user")
def increase_qty(cart_id):

    item = Cart.query.get(cart_id)
    item.quantity += 1
    db.session.commit()

    return redirect(url_for("view_cart"))

@app.route("/user/decrease/<int:cart_id>")
@login_required
@role_required("user")
def decrease_qty(cart_id):

    item = Cart.query.get(cart_id)

    if item.quantity > 1:
        item.quantity -= 1
        db.session.commit()

    return redirect(url_for("view_cart"))

@app.route("/user/remove/<int:cart_id>")
@login_required
@role_required("user")
def remove_item(cart_id):

    item = Cart.query.get(cart_id)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("view_cart"))

@app.route("/user/checkout", methods=["GET", "POST"])
@login_required
@role_required("user")
def checkout():

    if request.method == "POST":

        payment_method = request.form["payment_method"]

        cart_items = Cart.query.filter_by(
            user_id=session["user_id"]
        ).all()

        if not cart_items:
            return render_template("message.html", message="Cart Empty", back_url=url_for("user_dashboard"))

        total_amount = 0

        # calculate total
        for item in cart_items:
            product = Product.query.get(item.product_id)
            total_amount += product.price * item.quantity

        # create order
        order = Order(
            user_id=session["user_id"],
            total_amount=total_amount,
            payment_method=payment_method,
            status="Received"
        )

        db.session.add(order)
        db.session.commit()

        # create order items
        for item in cart_items:
            product = Product.query.get(item.product_id)

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )

            db.session.add(order_item)

        # clear cart
        Cart.query.filter_by(
            user_id=session["user_id"]
        ).delete()

        db.session.commit()

        return redirect(url_for("order_success", order_id=order.id))

    return render_template("user/checkout.html")

@app.route("/user/success/<int:order_id>")
@login_required
@role_required("user")
def order_success(order_id):

    order = Order.query.get(order_id)

    return render_template(
        "user/success.html",
        order=order
    )

@app.route("/user/orders")
@login_required
@role_required("user")
def user_orders():

    orders = Order.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "user/orders.html", orders=orders)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- Database initialization (runs on startup) ---
with app.app_context():
    db.create_all()

    # seed categories
    if Category.query.count() == 0:
        categories = [
            "Catering",
            "Florist",
            "Decoration",
            "Lighting",
            "Photography",
            "Music & DJ",
            "Venue Booking",
            "Makeup & Styling"
        ]
        
        for c in categories:
            db.session.add(Category(name=c))

        db.session.commit()

    # seed admin user
    if not User.query.filter_by(email="admin@erp.com").first():
        admin = User(
            name="Admin",
            email="admin@erp.com",
            password="admin123",
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)