from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Farmer, Product, Order, Customer  # Import Customer model
from config import Config
from flask_migrate import Migrate 
import os

app = Flask(__name__)
app.config.from_object(Config)

# Path to store uploaded images
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Page
@app.route('/')
def home():
    return render_template('base.html')

# Farmer Signup Page
@app.route('/farmer_signup', methods=['GET', 'POST'])
def farmer_signup():
    if request.method == 'POST':
        farmer_name = request.form['farmer_name']
        mobile_no = request.form['mobile_no']
        district = request.form['district']
        village = request.form['village']
        city = request.form['city']
        state = request.form['state']
        acres_owned = request.form['acres_owned']
        annual_income = request.form['annual_income']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists
        existing_farmer = Farmer.query.filter_by(email=email).first()
        if existing_farmer:
            flash('Email already exists. Please log in.')
            return redirect(url_for('farmer_login'))

        # Create a new farmer and save to the database
        new_farmer = Farmer(
            name=farmer_name, mobile_no=mobile_no, district=district,
            village=village, city=city, state=state,
            acres_owned=acres_owned, annual_income=annual_income,
            email=email, password=password
        )
        db.session.add(new_farmer)
        db.session.commit()

        flash('Signup Successful! Please log in.')
        return redirect(url_for('farmer_login'))

    return render_template('signup.html')

# Farmer Login Page
@app.route('/farmer_login', methods=['GET', 'POST'])
def farmer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the farmer exists in the database
        farmer = Farmer.query.filter_by(email=email, password=password).first()
        if farmer:
            session['farmer_id'] = farmer.farmer_id  # Store farmer_id in session
            flash('Login Successful!')
            return redirect(url_for('farmer_dashboard'))  # Redirect to dashboard after login
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('farmer_login'))

    return render_template('login.html')

# Farmer Dashboard
@app.route('/farmer_dashboard', methods=['GET'])
def farmer_dashboard():
    farmer_id = session.get('farmer_id')  # Get the logged-in farmer's ID
    if farmer_id is None:
        flash('Please log in to access your dashboard.')
        return redirect(url_for('farmer_login'))
    
    products = Product.query.filter_by(farmer_id=farmer_id).all()  # Fetch products for the logged-in farmer
    return render_template('farmer_dashboard.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    farmer_id = session.get('farmer_id')
    if farmer_id is None:
        flash('Please log in to add products.')
        return redirect(url_for('farmer_login'))

    if request.method == 'POST':
        name = request.form['name']
        image_file = request.files.get('image')  # Safely get the image file
        cost = request.form['cost']
        quantity = request.form['quantity']

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure the upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            image_file.save(image_path)

            # Store image path relative to the static folder
            relative_image_path = os.path.join('static/images', filename)

            new_product = Product(
                farmer_id=farmer_id,
                name=name,
                image=relative_image_path,  # Save the relative path to the database
                cost=cost,
                quantity=quantity
            )
            db.session.add(new_product)
            db.session.commit()

            flash('Product added successfully!')
            return redirect(url_for('farmer_dashboard'))
        else:
            flash('Invalid image file or no image uploaded.')

    return render_template('add_product.html')


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    farmer_id = session.get('farmer_id')
    if farmer_id is None:
        flash('Please log in to edit products.')
        return redirect(url_for('farmer_login'))

    product = Product.query.get(product_id)
    if product is None or product.farmer_id != farmer_id:
        flash('Product not found or you do not have permission to edit it.')
        return redirect(url_for('farmer_dashboard'))

    if request.method == 'POST':
        product.name = request.form['name']
        image_file = request.files.get('image')  # Safely get the image file
        product.cost = request.form['cost']
        product.quantity = request.form['quantity']

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure the upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            image_file.save(image_path)
            product.image = os.path.join('static/images', filename)  # Update with relative path

        db.session.commit()

        flash('Product updated successfully!')
        return redirect(url_for('farmer_dashboard'))

    return render_template('edit_product.html', product=product)

# Delete Product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    farmer_id = session.get('farmer_id')
    if farmer_id is None:
        flash('Please log in to delete products.')
        return redirect(url_for('farmer_login'))

    product = Product.query.get(product_id)
    if product and product.farmer_id == farmer_id:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!')
    else:
        flash('Product not found or you do not have permission to delete it.')

    return redirect(url_for('farmer_dashboard'))

# View Customer Orders Page
@app.route('/customer_orders', methods=['GET'])
def customer_orders():
    farmer_id = session.get('farmer_id')
    if farmer_id is None:
        flash('Please log in to view your orders.')
        return redirect(url_for('farmer_login'))

    orders = Order.query.join(Product).filter(Product.farmer_id == farmer_id).all()
    return render_template('customer_orders.html', orders=orders)


# Customer Signup Page
@app.route('/customer_signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        # Get customer details from form
        name = request.form.get('name')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        password = request.form.get('password')

        # Validate form inputs
        if not all([name, email, phone_no, address, password]):
            flash('Please fill in all fields.')
            return redirect(url_for('customer_signup'))

        # Check if the email already exists
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email already exists. Please log in.')
            return redirect(url_for('customer_login'))

        # Create a new customer and save to the database
        new_customer = Customer(
            name=name, 
            email=email, 
            phone_no=phone_no, 
            address=address, 
            password=generate_password_hash(password)  # Hash the password
        )
        db.session.add(new_customer)
        db.session.commit()

        flash('Signup successful! Please log in.')
        return redirect(url_for('customer_login'))

    return render_template('customer_signup.html')

# Customer Login Page
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate form inputs
        if not email or not password:
            flash('Please fill in all fields.')
            return redirect(url_for('customer_login'))

        # Check if the customer exists in the database
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):  # Check hashed password
            session['customer_id'] = customer.customer_id  # Store customer_id in session
            flash('Login successful!')
            return redirect(url_for('customer_dashboard'))  # Redirect to customer dashboard after login
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('customer_login'))

    return render_template('customer_login.html')

# Customer Dashboard
@app.route('/customer_dashboard', methods=['GET'])
def customer_dashboard():
    customer_id = session.get('customer_id')  # Get the logged-in customer's ID
    if customer_id is None:
        flash('Please log in to access your dashboard.')
        return redirect(url_for('customer_login'))

    # Display available products for the customer
    products = Product.query.all()
    return render_template('customer_dashboard.html', products=products)

# Serve static files (for image files)
@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Logout
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Clear session data
    flash('You have been logged out.')
    return redirect(url_for('home'))

# Error Handling
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
