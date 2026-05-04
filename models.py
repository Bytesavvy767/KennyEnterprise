from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# instantiate SQLAlchemy without app for circular import resolution

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_path = db.Column(db.String(255))
    category_id = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.name}>"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_phone = db.Column(db.String(32))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='orders')

    def __repr__(self):
        return f"<Order {self.id} - {self.product_id}>"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"<User {self.username}>"
