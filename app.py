from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Product, Order, User
from admin import init_admin

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize database and admin
db.init_app(app)
with app.app_context():
    init_admin(app, db)

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/checkout', methods=['POST'])
def checkout():
    # Dummy checkout route that would interact with M-Pesa
    data = request.form
    phone = data.get('phone')
    product_id = data.get('product_id')
    product = Product.query.get_or_404(product_id)

    # create order record before initiating payment
    order = Order(user_phone=phone, product_id=product.id, amount=product.price)
    db.session.add(order)
    db.session.commit()

    # send STK push via M-Pesa
    from mpesa import stk_push
    try:
        response = stk_push(phone, product.price, account_ref=str(order.id), description=product.name)
        flash('Payment initiated. Check your phone for confirmation.')
    except Exception as e:
        flash(f'Payment error: {e}')
    return redirect(url_for('index'))

# Endpoint for M-Pesa callback
@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    # Safaricom will POST transaction details here
    payload = request.get_json() or {}
    # Example payload processing; actual structure depends on the API response
    # You would extract the MerchantRequestID or CheckoutRequestID to match the order
    # and update the status accordingly.
    # For sandbox/testing purposes we just print it and return success.
    print('MPESA CALLBACK RECEIVED:', payload)
    # TODO: map payload to order and update status
    return jsonify({'status': 'received'})

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'image_path': product.image_path,
            'quantity': 1
        }
    
    session['cart'] = cart
    session.modified = True
    
    flash(f'{product.name} added to cart!')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        session.modified = True
        flash('Item removed from cart!')
    return redirect(url_for('cart'))

@app.route('/checkout_cart', methods=['POST'])
def checkout_cart():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!')
        return redirect(url_for('cart'))
    
    phone = request.form.get('phone')
    if not phone:
        flash('Please provide a phone number!')
        return redirect(url_for('cart'))
    
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Create orders for each cart item
    for item in cart.values():
        for _ in range(item['quantity']):
            order = Order(user_phone=phone, product_id=item['id'], amount=item['price'])
            db.session.add(order)
    
    db.session.commit()
    
    # Clear cart
    session.pop('cart', None)
    
    # Process payment for total amount
    from mpesa import stk_push
    try:
        response = stk_push(phone, total_amount, account_ref=f"cart_{phone}", description=f"Cart checkout - {len(cart)} items")
        flash('Payment initiated for all items in cart. Check your phone for confirmation.')
    except Exception as e:
        flash(f'Payment error: {e}')
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
    print('Initialized the database.')

@app.cli.command('seed-data')
def seed_data():
    """Seed the database with some example products."""
    from models import Product
    with app.app_context():
        if Product.query.count() == 0:
            items = [
                Product(name='Widget A', description='A useful widget', price=9.99, image_path='widget-a.jpg'),
                Product(name='Widget B', description='Another widget', price=14.99, image_path='widget-b.jpg'),
                Product(name='Gadget', description='A fancy gadget', price=29.99, image_path='gadget.jpg'),
            ]
            db.session.bulk_save_objects(items)
            db.session.commit()
            print('Seeded example products.')
        else:
            print('Products already exist, skipping.')


if __name__ == '__main__':
    app.run(debug=True)
