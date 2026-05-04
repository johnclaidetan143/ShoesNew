import os
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    login_required,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from forms import (
    LoginForm,
    RegisterForm,
    SearchForm,
    QuantityForm,
    CartUpdateForm,
    CheckoutForm,
    AddressForm,
    PasswordChangeForm,
    NotificationSettingsForm,
    PrivacyForm,
    ProductForm,
)
from models import db, User, Product, CartItem, Order, OrderItem, Notification, Rating, ContactMessage


load_dotenv(override=False)

def _send_email(to_email, subject, body):
    gmail_user = os.getenv("GMAIL_USER", "").strip()
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    if not gmail_user or not gmail_pass:
        print(f"[EMAIL] Not configured. Content: {body}")
        return False
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as s:
            s.login(gmail_user, gmail_pass)
            s.sendmail(gmail_user, to_email, msg.as_string())
        print(f"[EMAIL] Sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] Failed: {e}")
        return False


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dreamshoe-secret")
database_url = (os.getenv("DATABASE_URL") or "").strip()
if not database_url:
    database_url = "sqlite:////tmp/dreamshoe.db"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
if database_url.startswith("postgresql://") and "+pg8000" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_TIME_LIMIT"] = None
app.config["WTF_CSRF_EXEMPT_LIST"] = ["/cart/remove"]

db.init_app(app)


def _seed_db():
    """Seed default users and products if DB is empty. Safe to call multiple times."""
    if Product.query.first():
        return
    admin = User(name="Admin", email="admin@dreamshoe.com", phone="+1234567890")
    admin.set_password("admin@123")
    customer = User(name="Samantha Hope", email="customer@example.com", phone="+0987654321")
    customer.set_password("customer@123")
    db.session.add_all([admin, customer])
    db.session.flush()
    db.session.add(Notification(user_id=customer.id, message="Welcome to The Dream Shoe - Barili!"))
    products = [
        Product(name="GT Cut 3", category="Basketball", price=3499.99, stock=30, description="Designed for the game's biggest moments with full-length cushioning.", image_url="/static/images/Gt Cut.png"),
        Product(name="Ja Morant 3", category="Basketball", price=2999.99, stock=25, description="Built for explosive guards with Lightstrike Pro cushioning.", image_url="/static/images/JaMorant3_basketball.png"),
        Product(name="Jordan Luka 2", category="Basketball", price=2799.99, stock=35, description="Built for playmakers with responsive cushioning and wide base.", image_url="/static/images/jordanluka_basketball.png"),
        Product(name="Kobe 9", category="Basketball", price=3199.99, stock=28, description="Low-profile design for speed and precision on the court.", image_url="/static/images/KOBE 9_basketball.png"),
        Product(name="Nike Sabrina 2", category="Basketball", price=2599.99, stock=32, description="Lightweight foam cushioning for explosive lateral movement.", image_url="/static/images/sabrina2_basketball.png"),
        Product(name="Jordan Tatum 2", category="Basketball", price=2899.99, stock=28, description="Engineered for versatile forwards with all-around court dominance.", image_url="/static/images/tatum_basketball.png"),
        Product(name="Curry 13", category="Basketball", price=3099.99, stock=30, description="Stephen Curry's signature shoe built for elite shooting and quick cuts.", image_url="/static/images/Curry13_basketball.png"),
        Product(name="Nike Sabrina 3", category="Basketball", price=2699.99, stock=27, description="Next-gen Sabrina with improved lockdown fit and court feel.", image_url="/static/images/Sabrina3_basketball.png"),
        Product(name="Nike Air Zoom Pegasus 40", category="Running", price=2599.99, stock=50, description="Smooth responsive ride for everyday runners with Zoom Air cushioning.", image_url="/static/images/Men%27s%20Nike%20ACG%20Pegasus%20Trail_running.png"),
        Product(name="Adidas Ultraboost 23", category="Running", price=3299.99, stock=40, description="Incredible energy return with Boost midsole technology.", image_url="/static/images/T%C3%AAnis%20Nike%20Revolution%205_running.png"),
        Product(name="New Balance Fresh Foam 1080", category="Running", price=2899.99, stock=35, description="Maximum cushioning for long-distance runners.", image_url="/static/images/Chaussures%20de%20running%20Skyrocket%20Lite%20PUMA%20Black%20White_running.png"),
        Product(name="ASICS Gel-Nimbus 25", category="Running", price=2799.99, stock=45, description="Premium cushioning and stability for everyday runners.", image_url="/static/images/Asics%20Mens%20Gel%20Nimbus%2027%20Road_running.png"),
        Product(name="Nike Metcon 9", category="Training", price=2499.99, stock=55, description="The ultimate cross-training shoe with flat stable heel.", image_url="/static/images/Nike%20Metcon%209_training.png"),
        Product(name="Reebok Nano X3", category="Training", price=2299.99, stock=48, description="Built for the toughest workouts with stability and flexibility.", image_url="/static/images/Brooks%20Men%27s%20Trace%203_training.png"),
        Product(name="Adidas Powerlift 5", category="Training", price=2699.99, stock=40, description="Engineered for powerlifters with elevated heel and firm midsole.", image_url="/static/images/FitVille%20Extra%20Wide%20Shoes_training.png"),
        Product(name="Puma Fuse 2.0", category="Training", price=2199.99, stock=60, description="Versatile training shoe ideal for HIIT and circuit training.", image_url="/static/images/PUMA%20Neutron%20Men%27s%20Training%20Shoes_training.png"),
        Product(name="Nike Mercurial Vapor 15", category="Football", price=3999.99, stock=20, description="Designed for speed with lightweight upper and all-weather grip.", image_url="/static/images/Adidas%20footballshoes_football.png"),
        Product(name="Adidas Predator Accuracy", category="Football", price=3599.99, stock=22, description="Precision and control with rubber elements for enhanced grip.", image_url="/static/images/Adidas%20Jude%20Bellingham_football.png"),
        Product(name="Puma Future 7 Pro", category="Football", price=3299.99, stock=18, description="Adaptive fit with FUZIONFIT+ compression band.", image_url="/static/images/PUMA%20ATTACANTO%20II_football.png"),
        Product(name="New Balance Furon v7", category="Football", price=2999.99, stock=25, description="Speed-focused boot with seamless knit upper.", image_url="/static/images/PUMA%20Mens%20Ultra_football.png"),
        Product(name="Adidas Copa Mundial", category="Football", price=2799.99, stock=30, description="Legendary football boot with premium kangaroo leather upper.", image_url="/static/images/adidas%20Copa%20Mundial_football.png"),
        Product(name="Nike Air Max 270", category="Lifestyle", price=2499.99, stock=65, description="Iconic lifestyle sneaker with the largest Air unit ever.", image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"),
        Product(name="Adidas Stan Smith", category="Lifestyle", price=2199.99, stock=80, description="A timeless classic with clean leather upper.", image_url="https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&q=80"),
        Product(name="Puma RS-X", category="Lifestyle", price=2399.99, stock=55, description="Retro-inspired chunky sneaker with bold color blocking.", image_url="https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=400&q=80"),
        Product(name="New Balance 574", category="Lifestyle", price=2099.99, stock=70, description="A heritage classic reimagined for modern streets.", image_url="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80"),
    ]
    db.session.add_all(products)
    db.session.commit()

@app.before_request
def create_tables():
    db.create_all()
    _seed_db()

csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."

CATEGORIES = ["Running", "Basketball", "Training", "Football", "Lifestyle"]
ADMIN_EMAIL = "admin@dreamshoe.com"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_common_data():
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = (
            db.session.query(db.func.coalesce(db.func.sum(CartItem.quantity), 0))
            .filter(CartItem.user_id == current_user.id)
            .scalar()
            or 0
        )
    return {
        "categories": CATEGORIES,
        "cart_count": cart_count,
        "current_year": datetime.utcnow().year,
    }


@app.route("/")
def index():
    form = SearchForm()
    trending = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template("index.html", form=form, trending=trending)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    next_url = request.args.get("next") or request.form.get("next")
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back to The Dream Shoe - Barili!", "success")
            return redirect(next_url if next_url else url_for("home"))
        flash("Invalid email or password.", "error")
    return render_template("login.html", form=form, next_url=next_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegisterForm()
    next_url = request.args.get("next") or request.form.get("next")
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing:
            flash("This email is already registered.", "error")
        else:
            user = User(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
                phone=form.phone.data.strip() if form.phone.data else None,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            otp = str(random.randint(100000, 999999))
            try:
                user.otp_code = otp
                user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
                user.is_verified = False
                db.session.commit()
            except Exception as e:
                print(f"[REGISTER] OTP save error: {e}")
                db.session.rollback()
            sent = _send_email(
                user.email,
                "Your Verification Code - Shoes",
                f"Hi {user.name},\n\nYour verification code is: {otp}\n\nExpires in 10 minutes.\n\n-- Shoes Team"
            )
            if sent:
                flash("Account created! Check your email for the verification code.", "success")
            else:
                flash(f"Account created! Your OTP is: {otp}", "warning")
            session["pending_email"] = user.email
            session.permanent = True
            return redirect(url_for("verify_otp", email=user.email))
    return render_template("register.html", form=form, next_url=next_url)


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = (session.get("pending_email") or request.args.get("email","") or request.form.get("email","")).strip().lower()
    if not email:
        flash("Session expired. Please register again.", "error")
        return redirect(url_for("register"))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("register"))
    try:
        if user.is_verified:
            session.pop("pending_email", None)
            login_user(user)
            return redirect(url_for("home"))
    except Exception:
        pass
    session["pending_email"] = email
    session.permanent = True
    if request.method == "POST":
        entered = request.form.get("otp","").strip()
        try:
            saved = (user.otp_code or "").strip()
            expiry = user.otp_expiry
        except Exception:
            saved, expiry = "", None
        print(f"[OTP] entered={entered!r} saved={saved!r}")
        if not saved or not expiry:
            flash("OTP not found. Click Resend.", "error")
        elif datetime.utcnow() > expiry:
            flash("OTP expired. Click Resend.", "error")
        elif entered != saved:
            flash("Incorrect OTP. Try again.", "error")
        else:
            try:
                user.is_verified = True
                user.otp_code = None
                user.otp_expiry = None
                db.session.commit()
            except Exception as e:
                print(f"[OTP] DB error: {e}")
                db.session.rollback()
            session.pop("pending_email", None)
            login_user(user)
            flash("Email verified! Welcome to Shoes!", "success")
            return redirect(url_for("home"))
    return render_template("verify_otp.html", email=email)


@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = (session.get("pending_email") or request.form.get("email","")).strip().lower()
    user = User.query.filter_by(email=email).first()
    if user:
        otp = str(random.randint(100000, 999999))
        try:
            user.otp_code = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()
        except Exception:
            db.session.rollback()
        sent = _send_email(user.email, "Your New OTP - Shoes", f"Your new OTP is: {otp}\n\nExpires in 10 minutes.")
        flash(f"New OTP sent!" if sent else f"OTP: {otp} (email failed)", "success" if sent else "warning")
    return redirect(url_for("verify_otp", email=email))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            otp = str(random.randint(100000, 999999))
            try:
                user.otp_code = otp
                user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
                db.session.commit()
            except Exception:
                db.session.rollback()
            sent = _send_email(user.email, "Password Reset Code - Shoes", f"Hi {user.name},\n\nYour password reset code is: {otp}\n\nExpires in 10 minutes.\n\n-- Shoes Team")
            flash("Reset code sent to your email." if sent else f"Reset code: {otp} (email failed)", "success" if sent else "warning")
            session["reset_email"] = email
            session.permanent = True
            return redirect(url_for("reset_password"))
        flash("If that email exists, a reset code was sent.", "success")
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = (session.get("reset_email") or request.args.get("email","")).strip().lower()
    if not email:
        return redirect(url_for("forgot_password"))
    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for("forgot_password"))
    if request.method == "POST":
        entered = request.form.get("otp","").strip()
        new_pw = request.form.get("password","").strip()
        confirm_pw = request.form.get("confirm_password","").strip()
        try:
            saved = (user.otp_code or "").strip()
            expiry = user.otp_expiry
        except Exception:
            saved, expiry = "", None
        if not saved or not expiry:
            flash("Code not found. Request a new one.", "error")
        elif datetime.utcnow() > expiry:
            flash("Code expired. Request a new one.", "error")
        elif entered != saved:
            flash("Incorrect code. Try again.", "error")
        elif len(new_pw) < 6:
            flash("Password must be at least 6 characters.", "error")
        elif new_pw != confirm_pw:
            flash("Passwords do not match.", "error")
        else:
            user.set_password(new_pw)
            try:
                user.otp_code = None
                user.otp_expiry = None
                db.session.commit()
            except Exception:
                db.session.rollback()
            session.pop("reset_email", None)
            flash("Password reset! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("reset_password.html", email=email)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/home")
def home():
    active_category = request.args.get("category", "")
    search_query = request.args.get("q", "")
    sort = request.args.get("sort", "newest")
    products = Product.query
    if search_query:
        search_term = f"%{search_query}%"
        products = products.filter(
            Product.name.ilike(search_term) | Product.description.ilike(search_term)
        )
    elif active_category in CATEGORIES:
        products = products.filter_by(category=active_category)
    if sort == "price_asc":
        products = products.order_by(Product.price.asc())
    elif sort == "price_desc":
        products = products.order_by(Product.price.desc())
    else:
        products = products.order_by(Product.created_at.desc())
    products = products.all()
    search_form = SearchForm(query=search_query)
    return render_template(
        "shop.html",
        products=products,
        active_category=active_category,
        search_form=search_form,
    )


@app.route("/category/<category>")
def category_page(category):
    if category not in CATEGORIES:
        return redirect(url_for('home'))
    products = Product.query.filter_by(category=category).order_by(Product.created_at.desc()).all()
    return render_template("category.html", products=products, category=category)


@app.route("/seed-shoe")
def seed_shoe():
    from urllib.parse import quote
    def img(filename):
        return "/static/images/" + quote(filename)
    db.drop_all()
    db.create_all()

    admin = User(name="Admin User", email="admin@dreamshoe.com", phone="+1234567890")
    admin.set_password("admin@123")
    db.session.add(admin)

    customer = User(name="Samantha Hope", email="customer@example.com", phone="+0987654321")
    customer.set_password("customer@123")
    db.session.add(customer)
    db.session.flush()
    db.session.add(Notification(user_id=customer.id, message="Welcome to The Dream Shoe - Barili! Find your perfect pair."))

    products = [
        Product(name="Nike Air Zoom Pegasus 40", category="Running", price=2599.99, stock=50, description="The Nike Air Zoom Pegasus 40 delivers a smooth, responsive ride for everyday runners.", image_url="/static/images/Men%27s%20Nike%20ACG%20Pegasus%20Trail_running.png"),
        Product(name="Adidas Ultraboost 23", category="Running", price=3299.99, stock=40, description="Experience incredible energy return with Adidas Ultraboost 23.", image_url=img("Tênis Nike Revolution 5_running.png")),
        Product(name="New Balance Fresh Foam 1080", category="Running", price=2899.99, stock=35, description="Maximum cushioning for long-distance runners.", image_url=img("Chaussures de running Skyrocket Lite PUMA Black White_running.png")),
        Product(name="ASICS Gel-Nimbus 25", category="Running", price=2799.99, stock=45, description="Premium cushioning and stability for everyday runners.", image_url=img("Asics Mens Gel Nimbus 27 Road_running.png")),
        Product(name="GT Cut 3", category="Basketball", price=3499.99, stock=30, description="Designed for the game's biggest moments with full-length cushioning.", image_url=img("Gt Cut.png")),
        Product(name="Ja Morant 3", category="Basketball", price=2999.99, stock=25, description="Built for explosive guards with Lightstrike Pro cushioning.", image_url=img("JaMorant3_basketball.png")),
        Product(name="Jordan Luka 2", category="Basketball", price=2799.99, stock=35, description="Built for playmakers with responsive cushioning and wide base.", image_url=img("jordanluka_basketball.png")),
        Product(name="Kobe 9", category="Basketball", price=3199.99, stock=28, description="Low-profile design for speed and precision on the court.", image_url=img("KOBE 9_basketball.png")),
        Product(name="Nike Sabrina 2", category="Basketball", price=2599.99, stock=32, description="Lightweight foam cushioning for explosive lateral movement.", image_url=img("sabrina2_basketball.png")),
        Product(name="Jordan Tatum 2", category="Basketball", price=2899.99, stock=28, description="Engineered for versatile forwards with all-around court dominance.", image_url=img("tatum_basketball.png")),
        Product(name="Curry 13", category="Basketball", price=3099.99, stock=30, description="Stephen Curry's signature shoe built for elite shooting and quick cuts.", image_url=img("Curry13_basketball.png")),
        Product(name="Nike Sabrina 3", category="Basketball", price=2699.99, stock=27, description="Next-gen Sabrina with improved lockdown fit and court feel.", image_url=img("Sabrina3_basketball.png")),
        Product(name="Nike Metcon 9", category="Training", price=2499.99, stock=55, description="The ultimate cross-training shoe with flat stable heel.", image_url="/static/images/Nike%20Metcon%209_training.png"),
        Product(name="Brooks Glycerin 21", category="Training", price=3799.99, stock=40, description="Maximum cushioning for long training sessions with plush, soft landings.", image_url=img("Brooks Men's Glycerin 21_training.png")),
        Product(name="Reebok Nano X4", category="Training", price=2899.99, stock=45, description="Built for versatility with a stable base for lifting and flexible forefoot for cardio.", image_url=img("Reebok Nano X4.jpg")),
        Product(name="Under Armour TriBase Reign 6", category="Training", price=2699.99, stock=38, description="Designed for heavy lifting with a wide, flat base and superior grip for gym performance.", image_url=img("UNDER ARMOUR.jpg")),
        Product(name="Reebok Nano X3", category="Training", price=2299.99, stock=48, description="Built for the toughest workouts with stability and flexibility.", image_url="/static/images/Brooks%20Men%27s%20Trace%203_training.png"),
        Product(name="Adidas Powerlift 5", category="Training", price=2699.99, stock=40, description="Engineered for powerlifters with elevated heel and firm midsole.", image_url=img("FitVille Extra Wide Shoes_training.png")),
        Product(name="Puma Fuse 2.0", category="Training", price=2199.99, stock=60, description="Versatile training shoe ideal for HIIT and circuit training.", image_url="/static/images/PUMA%20Neutron%20Men%27s%20Training%20Shoes_training.png"),
        Product(name="Adidas Predator Accuracy", category="Football", price=3599.99, stock=22, description="Precision and control with rubber elements for enhanced grip.", image_url=img("Adidas Jude Bellingham_football.png")),
        Product(name="Puma Future 7 Pro", category="Football", price=3299.99, stock=18, description="Adaptive fit with FUZIONFIT+ compression band.", image_url=img("PUMA ATTACANTO II_football.png")),
        Product(name="New Balance Furon v7", category="Football", price=2999.99, stock=25, description="Speed-focused boot with seamless knit upper.", image_url=img("PUMA Mens Ultra_football.png")),
        Product(name="Adidas Copa Mundial", category="Football", price=2799.99, stock=30, description="Legendary football boot with premium kangaroo leather upper.", image_url=img("adidas Copa Mundial_football.png")),
        Product(name="Nike Air Max 270", category="Lifestyle", price=2499.99, stock=65, description="Iconic lifestyle sneaker with the largest Air unit ever.", image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"),
        Product(name="Adidas Stan Smith", category="Lifestyle", price=2199.99, stock=80, description="A timeless classic with clean leather upper.", image_url="https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&q=80"),
        Product(name="Puma RS-X", category="Lifestyle", price=2399.99, stock=55, description="Retro-inspired chunky sneaker with bold color blocking.", image_url="https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=400&q=80"),
        Product(name="New Balance 574", category="Lifestyle", price=2099.99, stock=70, description="A heritage classic reimagined for modern streets.", image_url="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80"),
    ]
    db.session.add_all(products)
    db.session.commit()

    total = Product.query.count()
    bball = Product.query.filter_by(category="Basketball").count()
    return f"<h2>✅ Seeded! Total: {total} products, Basketball: {bball}</h2><br><a href='/home?category=Basketball'>View Basketball</a> | <a href='/'>Go Home</a>"


@app.route("/fix-glycerin-image")
def fix_glycerin_image():
    p = Product.query.filter(Product.name.ilike('%glycerin%')).first()
    if p:
        p.image_url = "/static/images/Brooks%20Mens%20Glycerin%2021_training.png"
        db.session.commit()
        return f"Fixed: {p.name} → {p.image_url}"
    return "Product not found"


@app.route("/size-guide")
def prescriptions():
    return render_template("prescriptions.html", title="Size Guide")


@app.route("/style-advice")
def consult():
    return render_template("consult.html", title="Style Advice")


@app.route("/categories")
def categories():
    from sqlalchemy import func
    counts = db.session.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
    category_counts = {cat: count for cat, count in counts}
    total_count = sum(category_counts.values())
    trending = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template("categories.html", category_counts=category_counts, total_count=total_count, trending=trending)


@app.route("/search", methods=["GET", "POST"])
def search():
    search_form = SearchForm()
    category = request.args.get("category", "Running")
    if search_form.validate_on_submit():
        return redirect(url_for("search", q=search_form.query.data.strip(), category=category))
    query_text = request.args.get("q", "").strip()
    if query_text:
        search_term = f"%{query_text}%"
        results = Product.query.filter(
            Product.name.ilike(search_term) | Product.description.ilike(search_term)
        ).all()
    else:
        results = Product.query.filter_by(category=category).all() if category in CATEGORIES else []
    search_form.query.data = query_text
    return render_template("search.html", results=results, search_form=search_form, active_category=category, query_text=query_text)


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    form = QuantityForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in to add items to your cart.", "error")
            return redirect(url_for("login", next=request.url))
        quantity = form.quantity.data
        if quantity > product.stock:
            flash("Quantity exceeds available stock.", "error")
        else:
            item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
            if item:
                item.quantity = min(item.quantity + quantity, product.stock)
            else:
                item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity, size=form.size.data)
                db.session.add(item)
            db.session.commit()
            flash(f"Added {quantity} pair(s) to your cart.", "success")
            return redirect(url_for("cart"))
    return render_template("product.html", product=product, form=form)


@app.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal() for item in items) if items else 0.0
    total_qty = sum(item.quantity for item in items) if items else 0
    return render_template("cart.html", items=items, subtotal=subtotal, total_qty=total_qty)


@app.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    if request.form.get("remove"):
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "success")
        return redirect(url_for("cart"))
    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1
    if quantity < 1:
        flash("Quantity must be at least 1.", "error")
    elif quantity > item.product.stock:
        flash("Quantity exceeds available stock.", "error")
    else:
        item.quantity = quantity
        db.session.commit()
        flash("Cart updated successfully.", "success")
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    form = CheckoutForm()
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty. Add a product before checkout.", "error")
        return redirect(url_for("cart"))
    subtotal = sum(item.subtotal() for item in items)
    if form.validate_on_submit():
        try:
            current_user.address = (
                f"{form.address.data.strip()}, "
                f"{form.city.data.strip()}, "
                f"{form.zip_code.data.strip()}"
            )
            total = round(subtotal, 2)
            order = Order(user_id=current_user.id, total=total, status="Pending")
            db.session.add(order)
            db.session.flush()
            for item in items:
                if not item.product:
                    flash("One or more cart items are no longer available.", "error")
                    db.session.rollback()
                    return redirect(url_for("cart"))
                if item.quantity > item.product.stock:
                    flash(f"Not enough stock for {item.product.name}. Please update your cart.", "error")
                    db.session.rollback()
                    return redirect(url_for("cart"))
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                db.session.add(order_item)
            for item in items:
                db.session.delete(item)
            notification = Notification(
                user_id=current_user.id,
                message=f"Your order #{order.id} has been placed successfully.",
            )
            db.session.add(notification)
            db.session.commit()
            # Send order confirmation email
            try:
                items_text = "\n".join(
                    f"  - {oi.product.name} x{oi.quantity} = \u20b1{oi.line_total():.2f}"
                    for oi in order.items
                )
                body = (
                    f"Hi {current_user.name},\n\n"
                    f"Your order #{order.id} has been placed successfully!\n\n"
                    f"Items:\n{items_text}\n\n"
                    f"Total: \u20b1{order.total:.2f}\n"
                    f"Status: {order.status}\n\n"
                    f"Thank you for shopping at Shoes!\n\n-- Shoes Team"
                )
                _send_email(current_user.email, f"Order #{order.id} Confirmed - Shoes", body)
            except Exception as e:
                print(f"[ORDER EMAIL] Failed: {e}")
            flash("Your order has been placed successfully!", "success")
            return redirect(url_for("order_success"))
        except Exception:
            db.session.rollback()
            flash("We could not place your order right now. Please try again.", "error")
    if current_user.address:
        full_address = current_user.address.split(", ")
        if len(full_address) >= 4:
            form.address.data = full_address[0]
            form.city.data = full_address[1]
            form.zip_code.data = full_address[3]
        elif len(full_address) >= 3:
            form.address.data = full_address[0]
            form.city.data = full_address[1]
            form.zip_code.data = full_address[2]
        else:
            form.address.data = current_user.address
    elif request.method == "POST":
        flash("Please complete all required checkout fields.", "error")
    return render_template("checkout.html", form=form, items=items, subtotal=subtotal)


@app.route("/order-success")
@login_required
def order_success():
    return render_template("order_success.html")


@app.route("/order/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.status.lower() not in {"pending", "processing"}:
        flash("Only pending or processing orders can be cancelled.", "error")
        return redirect(url_for("history"))
    order.status = "Cancelled"
    db.session.add(Notification(user_id=current_user.id, message=f"Your order #{order.id} has been cancelled."))
    db.session.commit()
    flash("Your order has been cancelled and stock has been restored.", "success")
    return redirect(url_for("history"))


@app.route("/order/<int:order_id>/rate", methods=["POST"])
@login_required
def rate_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    existing = Rating.query.filter_by(order_id=order_id).first()
    if existing:
        flash("You have already rated this order.", "error")
        return redirect(url_for("history"))
    try:
        stars = int(request.form.get("stars", 0))
    except ValueError:
        stars = 0
    if not 1 <= stars <= 5:
        flash("Please select a rating between 1 and 5 stars.", "error")
        return redirect(url_for("history"))
    comment = request.form.get("comment", "").strip()
    db.session.add(Rating(user_id=current_user.id, order_id=order_id, stars=stars, comment=comment or None))
    db.session.commit()
    flash("Thank you for your rating! ⭐", "success")
    return redirect(url_for("history"))



@app.route("/order/<int:order_id>/confirm-received", methods=["POST"])
@login_required
def confirm_order_received(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.status.lower() != "processing":
        flash("Only orders that are being processed can be confirmed.", "error")
        return redirect(url_for("history"))
    order.status = "Completed"
    db.session.add(Notification(
        user_id=current_user.id,
        message=f"You confirmed receipt of order #{order.id}. Thank you!"
    ))
    db.session.commit()
    # Send confirmation email
    try:
        items_text = "\n".join(
            f"  - {oi.product.name} x{oi.quantity} = \u20b1{oi.line_total():.2f}"
            for oi in order.items
        )
        body = (
            f"Hi {current_user.name},\n\n"
            f"You have confirmed receipt of order #{order.id}.\n\n"
            f"Items:\n{items_text}\n\n"
            f"Total: \u20b1{order.total:.2f}\n"
            f"Status: Completed\n\n"
            f"Thank you for shopping at Shoes! We hope you love your purchase.\n\n-- Shoes Team"
        )
        _send_email(current_user.email, f"Order #{order.id} Completed - Shoes", body)
    except Exception as e:
        print(f"[CONFIRM EMAIL] Failed: {e}")
    flash(f"Order #{order.id} marked as completed. Thank you!", "success")
    return redirect(url_for("history"))

@app.route("/history")
@login_required
def history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("history.html", orders=orders)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    password_form = PasswordChangeForm()
    if password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash("Your password has been updated.", "success")
            return redirect(url_for("profile"))
        flash("Current password is incorrect.", "error")
    return render_template("profile.html", password_form=password_form)


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.route("/address", methods=["GET", "POST"])
@login_required
def address():
    form = AddressForm()
    if form.validate_on_submit():
        current_user.address = f"{form.address.data.strip()}, {form.city.data.strip()}, {form.state.data.strip()}, {form.zip_code.data.strip()}"
        db.session.commit()
        flash("Address has been saved.", "success")
        return redirect(url_for("address"))
    if current_user.address:
        full_address = current_user.address.split(", ")
        if len(full_address) >= 4:
            form.address.data = full_address[0]
            form.city.data = full_address[1]
            form.state.data = full_address[2]
            form.zip_code.data = full_address[3]
    return render_template("address.html", form=form)


@app.route("/notifications", methods=["GET", "POST"])
@login_required
def notifications():
    form = NotificationSettingsForm(
        notify_push=current_user.notify_push,
        notify_in_app=current_user.notify_in_app,
        notify_email=current_user.notify_email,
    )
    if form.validate_on_submit():
        current_user.notify_push = form.notify_push.data
        current_user.notify_in_app = form.notify_in_app.data
        current_user.notify_email = form.notify_email.data
        db.session.commit()
        flash("Notification settings updated.", "success")
        return redirect(url_for("notifications"))
    alerts = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", form=form, alerts=alerts)


@app.route("/privacy", methods=["GET", "POST"])
@login_required
def privacy():
    form = PrivacyForm(invisible_on_comments=current_user.invisible_on_comments)
    if form.validate_on_submit():
        current_user.invisible_on_comments = form.invisible_on_comments.data
        db.session.commit()
        flash("Privacy settings saved.", "success")
        return redirect(url_for("privacy"))
    return render_template("privacy.html", form=form)


@app.route("/community-rules")
def community_rules():
    return render_template("community_rules.html")



@app.route("/contact", methods=["GET", "POST"])
def contact():
    sent = False
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and subject and message:
            # Save to DB
            try:
                user_id = current_user.id if current_user.is_authenticated else None
                msg = ContactMessage(name=name, email=email, subject=subject, message=message, user_id=user_id)
                db.session.add(msg)
                db.session.commit()
            except Exception as e:
                print(f"[CONTACT] DB error: {e}")
                db.session.rollback()
            # Send email notification to admin
            body = (
                f"New contact message from Shoes website:\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Subject: {subject}\n\n"
                f"Message:\n{message}"
            )
            _send_email(os.getenv("GMAIL_USER", ""), f"[Shoes Contact] {subject}", body)
            sent = True
        else:
            flash("Please fill in all fields.", "error")
    # Show user's previous messages and replies
    user_messages = []
    if current_user.is_authenticated:
        from sqlalchemy import or_
        user_messages = ContactMessage.query.filter(
            or_(
                ContactMessage.user_id == current_user.id,
                ContactMessage.email == current_user.email
            )
        ).order_by(ContactMessage.created_at.desc()).all()
        # Backfill user_id for old messages matched by email
        for m in user_messages:
            if m.user_id is None:
                m.user_id = current_user.id
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    elif sent:
        # guest - just show sent confirmation
        pass
    return render_template("contact.html", sent=sent, user_messages=user_messages)

@app.route("/admin/contacts")
@login_required
def admin_contacts():
    denied = require_admin_access()
    if denied:
        return denied
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    unread = ContactMessage.query.filter_by(is_read=False).count()
    return render_template("admin/contacts.html", title="Contact Messages", messages=messages, unread=unread)


@app.route("/admin/contacts/<int:msg_id>/read", methods=["POST"])
@login_required
def admin_contact_read(msg_id):
    denied = require_admin_access()
    if denied:
        return denied
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for("admin_contacts"))



@app.route("/admin/contacts/<int:msg_id>/reply", methods=["POST"])
@login_required
def admin_contact_reply(msg_id):
    denied = require_admin_access()
    if denied:
        return denied
    msg = ContactMessage.query.get_or_404(msg_id)
    reply_message = request.form.get("reply_message", "").strip()
    if not reply_message:
        flash("Reply message cannot be empty.", "error")
        return redirect(url_for("admin_contacts"))
    body = (
        f"Hi {msg.name},\n\n"
        f"{reply_message}\n\n"
        f"---\n"
        f"This is a reply to your message:\n"
        f"Subject: {msg.subject}\n"
        f"Your message: {msg.message}\n\n"
        f"-- Shoes Team"
    )
    sent = _send_email(msg.email, f"Re: {msg.subject} - Shoes", body)
    if sent:
        msg.is_read = True
        db.session.commit()
        flash(f"Reply sent to {msg.name} ({msg.email}).", "success")
    else:
        flash("Failed to send reply. Check Gmail credentials.", "error")
    return redirect(url_for("admin_contacts"))

@app.route("/admin/contacts/<int:msg_id>/delete", methods=["POST"])
@login_required
def admin_contact_delete(msg_id):
    denied = require_admin_access()
    if denied:
        return denied
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.", "success")
    return redirect(url_for("admin_contacts"))


@app.route("/about")
def about():
    return render_template("about.html")


def is_admin_user(user):
    return bool(
        getattr(user, "is_authenticated", False)
        and (
            getattr(user, "email", "") == ADMIN_EMAIL
            or getattr(user, "role", "") == "admin"
        )
    )


def require_admin_access():
    if not is_admin_user(current_user):
        flash("Admin access only.", "error")
        return redirect(url_for("home"))
    return None


@app.route("/admin")
@login_required
def admin_root():
    denied = require_admin_access()
    if denied:
        return denied
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    denied = require_admin_access()
    if denied:
        return denied
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.coalesce(db.func.sum(Order.total), 0.0)).scalar() or 0.0
    return render_template(
        "admin/dashboard.html",
        title="Dashboard",
        recent_orders=recent_orders,
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
    )


@app.route("/admin/products")
@login_required
def admin_products():
    denied = require_admin_access()
    if denied:
        return denied
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", title="Products", products=products)


@app.route("/admin/products/new", methods=["GET", "POST"])
@login_required
def admin_product_new():
    denied = require_admin_access()
    if denied:
        return denied
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data.strip(),
            category=form.category.data,
            price=form.price.data,
            stock=form.stock.data,
            description=form.description.data.strip() if form.description.data else None,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"'{product.name}' added successfully.", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin/product_form.html", title="Add Product", form=form, product=None)


@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def admin_product_edit(product_id):
    denied = require_admin_access()
    if denied:
        return denied
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.category = form.category.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.description = form.description.data.strip() if form.description.data else None
        product.image_url = form.image_url.data.strip() if form.image_url.data else None
        db.session.commit()
        flash(f"'{product.name}' updated successfully.", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin/product_form.html", title="Edit Product", form=form, product=product)


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@login_required
def admin_product_delete(product_id):
    denied = require_admin_access()
    if denied:
        return denied
    product = Product.query.get_or_404(product_id)
    if product.order_items:
        flash("Cannot delete product with existing order history.", "error")
        return redirect(url_for("admin_products"))
    db.session.delete(product)
    db.session.commit()
    flash(f"'{product.name}' deleted.", "success")
    return redirect(url_for("admin_products"))


@app.route("/admin/orders")
@login_required
def admin_orders():
    denied = require_admin_access()
    if denied:
        return denied
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", title="Orders", orders=orders)


@app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
@login_required
def admin_order_status(order_id):
    denied = require_admin_access()
    if denied:
        return denied
    order = Order.query.get_or_404(order_id)
    new_status = (request.form.get("status") or "").strip()
    valid_statuses = {"Pending", "Processing", "Completed", "Cancelled"}
    if new_status not in valid_statuses:
        flash("Invalid order status.", "error")
        return redirect(url_for("admin_orders"))

    old_status = order.status
    if old_status == new_status:
        flash("Order status is already up to date.", "success")
        return redirect(url_for("admin_orders"))

    # Decrease stock only when first moving to Processing
    if new_status == "Processing" and old_status == "Pending":
        for item in order.items:
            if item.product.stock < item.quantity:
                flash(f"Insufficient stock for order #{order.id}.", "error")
                return redirect(url_for("admin_orders"))
        for item in order.items:
            item.product.stock -= item.quantity
            print(f"[STOCK] {item.product.name} stock: {item.product.stock + item.quantity} -> {item.product.stock}")

    order.status = new_status
    db.session.add(
        Notification(
            user_id=order.user_id,
            message=f"Your order #{order.id} status is now {new_status}.",
        )
    )
    db.session.commit()
    try:
        _send_email(
            order.user.email,
            f"Order #{order.id} Update - Shoes",
            f"Hi {order.user.name},\n\nYour order #{order.id} status has been updated to: {new_status}\n\nThank you for shopping at Shoes!\n\n-- Shoes Team"
        )
    except Exception as e:
        print(f"[STATUS EMAIL] Failed: {e}")
    flash(f"Order #{order.id} updated to {new_status}.", "success")
    return redirect(url_for("admin_orders"))


@app.route("/admin/users")
@login_required
def admin_users():
    denied = require_admin_access()
    if denied:
        return denied
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", title="Users", users=users)


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
def admin_user_delete(user_id):
    denied = require_admin_access()
    if denied:
        return denied
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own admin account.", "error")
        return redirect(url_for("admin_users"))
    if user.email == ADMIN_EMAIL:
        flash("Primary admin account cannot be deleted.", "error")
        return redirect(url_for("admin_users"))
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.name}' deleted.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/about")
@login_required
def admin_about():
    denied = require_admin_access()
    if denied:
        return denied
    return render_template("admin_about.html", title="Admin About")


@app.route("/admin/products/add", methods=["GET", "POST"])
@login_required
def admin_add_product():
    return admin_product_new()


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Product.query.first():
            admin = User(name="Admin", email="admin@dreamshoe.com", phone="+1234567890")
            admin.set_password("admin@123")
            customer = User(name="Samantha Hope", email="customer@example.com", phone="+0987654321")
            customer.set_password("customer@123")
            db.session.add_all([admin, customer])
            db.session.flush()
            db.session.add(Notification(user_id=customer.id, message="Welcome to The Dream Shoe - Barili!"))
            products = [
                Product(name="GT Cut 3", category="Basketball", price=199.99, stock=30, description="Designed for the game's biggest moments with full-length cushioning.", image_url="/static/images/Gt Cut.png"),
                Product(name="Ja Morant 3", category="Basketball", price=149.99, stock=25, description="Built for explosive guards with Lightstrike Pro cushioning.", image_url="/static/images/JaMorant3_basketball.png"),
                Product(name="Jordan Luka 2", category="Basketball", price=139.99, stock=35, description="Built for playmakers with responsive cushioning and wide base.", image_url="/static/images/jordanluka_basketball.png"),
                Product(name="Kobe 9", category="Basketball", price=159.99, stock=28, description="Low-profile design for speed and precision on the court.", image_url="/static/images/KOBE 9_basketball.png"),
                Product(name="Nike Sabrina 2", category="Basketball", price=129.99, stock=32, description="Lightweight foam cushioning for explosive lateral movement.", image_url="/static/images/sabrina2_basketball.png"),
                Product(name="Jordan Tatum 2", category="Basketball", price=144.99, stock=28, description="Engineered for versatile forwards with all-around court dominance.", image_url="/static/images/tatum_basketball.png"),
                Product(name="Curry 13", category="Basketball", price=159.99, stock=30, description="Stephen Curry's signature shoe built for elite shooting and quick cuts.", image_url="/static/images/Curry13_basketball.png"),
                Product(name="Nike Sabrina 3", category="Basketball", price=134.99, stock=27, description="Next-gen Sabrina with improved lockdown fit and court feel.", image_url="/static/images/Sabrina3_basketball.png"),
                Product(name="Nike Air Zoom Pegasus 40", category="Running", price=129.99, stock=50, description="Smooth responsive ride for everyday runners with Zoom Air cushioning.", image_url="/static/images/Men's Nike ACG Pegasus Trail_running.png"),
                Product(name="Adidas Ultraboost 23", category="Running", price=189.99, stock=40, description="Incredible energy return with Boost midsole technology.", image_url="/static/images/Tênis Nike Revolution 5_running.png"),
                Product(name="New Balance Fresh Foam 1080", category="Running", price=164.99, stock=35, description="Maximum cushioning for long-distance runners.", image_url="/static/images/Chaussures de running Skyrocket Lite PUMA Black White_running.png"),
                Product(name="ASICS Gel-Nimbus 25", category="Running", price=159.99, stock=45, description="Premium cushioning and stability for everyday runners.", image_url="/static/images/Asics Mens Gel Nimbus 27 Road_running.png"),
                Product(name="Nike Metcon 9", category="Training", price=129.99, stock=55, description="The ultimate cross-training shoe with flat stable heel.", image_url="/static/images/Nike%20Metcon%209_training.png"),
                Product(name="Reebok Nano X3", category="Training", price=134.99, stock=48, description="Built for the toughest workouts with stability and flexibility.", image_url="/static/images/Brooks Men's Trace 3_training.png"),
                Product(name="Adidas Powerlift 5", category="Training", price=109.99, stock=40, description="Engineered for powerlifters with elevated heel and firm midsole.", image_url="/static/images/FitVille Extra Wide Shoes_training.png"),
                Product(name="Puma Fuse 2.0", category="Training", price=89.99, stock=60, description="Versatile training shoe ideal for HIIT and circuit training.", image_url="/static/images/PUMA Neutron Men's Training Shoes_training.png"),
                Product(name="Nike Mercurial Vapor 15", category="Football", price=249.99, stock=20, description="Designed for speed with lightweight upper and all-weather grip.", image_url="/static/images/Adidas footballshoes_football.png"),
                Product(name="Adidas Predator Accuracy", category="Football", price=229.99, stock=22, description="Precision and control with rubber elements for enhanced grip.", image_url="/static/images/Adidas Jude Bellingham_football.png"),
                Product(name="Puma Future 7 Pro", category="Football", price=199.99, stock=18, description="Adaptive fit with FUZIONFIT+ compression band.", image_url="/static/images/PUMA ATTACANTO II_football.png"),
                Product(name="New Balance Furon v7", category="Football", price=179.99, stock=25, description="Speed-focused boot with seamless knit upper.", image_url="/static/images/PUMA Mens Ultra_football.png"),
                Product(name="Adidas Copa Mundial", category="Football", price=159.99, stock=30, description="Legendary football boot with premium kangaroo leather upper.", image_url="/static/images/adidas%20Copa%20Mundial_football.png"),
                Product(name="Nike Air Max 270", category="Lifestyle", price=149.99, stock=65, description="Iconic lifestyle sneaker with the largest Air unit ever.", image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"),
                Product(name="Adidas Stan Smith", category="Lifestyle", price=89.99, stock=80, description="A timeless classic with clean leather upper.", image_url="https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&q=80"),
                Product(name="Puma RS-X", category="Lifestyle", price=109.99, stock=55, description="Retro-inspired chunky sneaker with bold color blocking.", image_url="https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=400&q=80"),
                Product(name="New Balance 574", category="Lifestyle", price=99.99, stock=70, description="A heritage classic reimagined for modern streets.", image_url="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80"),
            ]
            db.session.add_all(products)
            db.session.commit()
            print(f"✅ Auto-seeded {Product.query.count()} products")
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)), debug=True)
