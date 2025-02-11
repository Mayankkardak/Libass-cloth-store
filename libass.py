from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__, static_folder="frontend", template_folder="frontend")

# Database Config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stich.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller = db.Column(db.String(100), nullable=False)

# Create Database
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

# Register Route
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = bcrypt.generate_password_hash(data.get("password")).decode("utf-8")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# Login Route
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Add Product Route
@app.route("/api/add_product", methods=["POST"])
def add_product():
    data = request.json
    name = data.get("name")
    price = data.get("price")
    seller = data.get("seller")

    new_product = Product(name=name, price=price, seller=seller)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

# Fetch Products Route
@app.route("/api/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    product_list = [{"id": p.id, "name": p.name, "price": p.price, "seller": p.seller} for p in products]
    return jsonify(product_list)

if __name__ == "__main__":
    app.run(debug=True)
