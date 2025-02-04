from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class Farmer(db.Model):
    __tablename__ = 'farmers'
    
    farmer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    acres_owned = db.Column(db.Numeric(10, 2), nullable=False)
    annual_income = db.Column(db.Numeric(10, 2), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, mobile_no, district, village, city, state, acres_owned, annual_income, email, password):
        self.name = name
        self.mobile_no = mobile_no
        self.district = district
        self.village = village
        self.city = city
        self.state = state
        self.acres_owned = acres_owned
        self.annual_income = annual_income
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<Farmer ID: {self.farmer_id}, Name: {self.name}>"

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = (UniqueConstraint('farmer_id', 'name', name='uix_farmer_name'),)

    farmer = db.relationship('Farmer', backref='products')

    def __init__(self, farmer_id, name, image, cost, quantity):
        self.farmer_id = farmer_id
        self.name = name
        self.image = image
        self.cost = cost
        self.quantity = quantity

    def __repr__(self):
        return f"<Product ID: {self.id}, Name: {self.name}, Farmer ID: {self.farmer_id}>"

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    ordered_quantity = db.Column(db.Integer, nullable=False)
    ordered_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    product = db.relationship('Product', backref='orders')
    customer = db.relationship('Customer', backref='orders')  # Keep the backref here

    def __init__(self, product_id, customer_id, ordered_quantity):
        self.product_id = product_id
        self.customer_id = customer_id
        self.ordered_quantity = ordered_quantity

    def __repr__(self):
        return f"<Order ID: {self.id}, Product ID: {self.product_id}, Customer ID: {self.customer_id}>"

class Customer(db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # No orders relationship here

    def __init__(self, name, email, phone_no, address, password):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.address = address
        self.password = password

    def __repr__(self):
        return f"<Customer ID: {self.customer_id}, Name: {self.name}>"
