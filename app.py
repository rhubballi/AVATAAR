from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///avatar_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # route name

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(250), nullable=True)  # optional

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create DB and sample products if not exist
def create_tables():
    db.create_all()
    if Product.query.count() == 0:
        demo = [
            {"slug":"talking-avatar", "title":"Talking Avatar", "description":"Type text and get a talking avatar video."},
            {"slug":"realtime-avatar", "title":"Real-time Avatar", "description":"Real-time voice-to-avatar conversation."},
            {"slug":"pdf-to-avatar", "title":"PDF → Avatar", "description":"Upload PDF, extract text and make avatars."},
            {"slug":"multilingual-avatar", "title":"Multilingual Avatar", "description":"Speak or type in multiple languages."}
        ]
        for p in demo:
            prod = Product(slug=p['slug'], title=p['title'], description=p['description'])
            db.session.add(prod)
        db.session.commit()

# Some Flask installations (or future versions) may not expose
# `before_first_request`; register a one-time initializer on
# `before_request` instead so it runs on the first incoming request.
_app_initialized = False

@app.before_request
def _ensure_initialized():
    global _app_initialized
    if _app_initialized:
        return
    try:
        create_tables()
    except Exception:
        # If DB isn't available yet, swallow the exception so the app can still start.
        # The error will surface on requests that need the DB.
        pass
    _app_initialized = True

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/products")
def products():
    prods = Product.query.all()
    return render_template("products.html", products=prods)

@app.route("/product/<slug>")
def product(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    # If user not logged in, redirect to login and pass next
    if not current_user.is_authenticated:
        next_url = url_for('product', slug=slug)
        return redirect(url_for('login', next=next_url))
    # Render product usage page
    return render_template("product.html", product=product)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        if not email or not password:
            flash("Please provide email and password.", "warning")
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash("Account already exists with that email.", "warning")
            return redirect(url_for('signup'))
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created. Logged in.", "success")
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard'))
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get('next')
            # Security: ensure next is internal
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('index'))

# Run
if __name__ == "__main__":
    app.run(debug=True)
