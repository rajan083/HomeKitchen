from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
import os
import datetime
from datetime import timedelta
from flask_mail import Mail, Message
from twilio.rest import Client
import uuid
import time
from decimal import Decimal
import qrcode
from werkzeug.utils import secure_filename
import secrets
import urllib.parse
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key= 'SecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/HomeKitchen'
db=SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'rm4952989@gmail.com'
app.config['MAIL_PASSWORD'] = 'reko dlfw jqzj bnlb'
app.config['MAIL_DEFAULT_SENDER'] = 'rm4952989@gmail.com'
mail = Mail(app)

verification_tokens={}



#=================================================UPLOAD FOLDER================================================


    
UPLOAD_FOLDER_ITEM = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER_ITEM):
    os.makedirs(UPLOAD_FOLDER_ITEM)

app.config['UPLOAD_FOLDER_ITEM'] = UPLOAD_FOLDER_ITEM




#=================================================USER-DATABASE================================================



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable= False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    upi_id = db.Column(db.String(50), nullable=True)
    location= db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(10), nullable=False)
    items = db.relationship('Item', backref='seller')
    created_at= db.Column(db.DateTime, default= datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    business_name = db.Column(db.String(150), nullable=True, unique=True)
    terms_accepted = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)  
    latitude = db.Column(db.String(50), nullable=True)
    longitude = db.Column(db.String(50), nullable=True)
    vehicle_type= db.Column(db.String(50), nullable= True)
    vehicle_number= db.Column(db.String(50), nullable=True)
    id_proof = db.Column(db.String(200), nullable=True)  # File path
    license = db.Column(db.String(200), nullable=True)  # File path
    insurance = db.Column(db.String(200), nullable=True)  # File path
    photo = db.Column(db.String(200), nullable=True)  # File path
    verified = db.Column(db.Boolean, default=False)
    wallet_balance= db.Column(db.Float, default=0.0)



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



#=================================================RIDER-DATABASE================================================



app.config['UPLOAD_FOLDER'] = 'static/UserInfo'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class Rider_kyc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable= False, unique=True)
    email = db.Column(db.String(120),nullable=False, unique=True)
    password_hash = db.Column(db.String(250), nullable=False)
    role= db.Column(db.String(20), nullable=False)
    created_at= db.Column(db.DateTime, default= datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)
    vehicle_type= db.Column(db.String(50), nullable= True)
    vehicle_number= db.Column(db.String(50), nullable=True)
    id_proof = db.Column(db.String(200), nullable=True)
    license = db.Column(db.String(200), nullable=True)
    insurance = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.String(200), nullable=True)
    verified = db.Column(db.Boolean, default=False)
    wallet_balance= db.Column(db.Float, default=0.0)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



#=================================================VENDOR-KYC================================================


class Vendor_kyc(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100), nullable=False)
    email= db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    id_number= db.Column(db.String(100), nullable=False)
    phone= db.Column(db.String(15), nullable=False, unique=True)
    id_proof= db.Column(db.String(255), nullable=False)
    photo_path= db.Column(db.String(255), nullable=False)
    business_name = db.Column(db.String(150), nullable=True, unique=True)
    verified = db.Column(db.Boolean, default=False)



    

#=================================================ITEM-DATABASE================================================



class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemid = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    context = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    type= db.Column(db.String(50), nullable= False)
    region= db.Column(db.String(100), nullable= True)
    dislikes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='item', lazy=True)
    categories = db.Column(db.String(50), nullable=True)
    order_count = db.Column(db.Integer, default=0)  


    

#=================================================ORDER================================================


    
class Order(db.Model):
    id= db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name= db.Column(db.String(100), nullable=False)
    user_email= db.Column(db.String(100), db.ForeignKey("user.email"), nullable=False)
    amount= db.Column(db.Float, nullable=False)
    upi_link= db.Column(db.String(500), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    payment_status= db.Column(db.String(20), default="Pending")
    consumer_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable= True)
    vendor_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable= True)
    rider_id= db.Column(db.Integer, db.ForeignKey('rider_kyc.id'), nullable= True)
    status = db.Column(db.String(20))
    delivered_at = db.Column(db.DateTime, nullable= True)
    rider_fee = db.Column(db.Float, default=0.0)
    delivery_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    consumer = db.relationship('User', primaryjoin="and_(Order.consumer_id == User.id, User.role == 'consumer')", backref='consumer_orders')
    vendor = db.relationship('User', primaryjoin="and_(Order.vendor_id == User.id, User.role == 'vendor')", backref='vendor_orders')
    rider = db.relationship('Rider_kyc', backref='rider_deliveries')
    
    
    
#=================================================TRANSACTION================================================

    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    consumer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    rider_id = db.Column(db.Integer, db.ForeignKey('rider_kyc.id'), nullable=True)  
    vendor_share = db.Column(db.Float, nullable=False, default=0.0)
    rider_share = db.Column(db.Float, nullable=False, default=0.0)
    platform_share = db.Column(db.Float, nullable=False, default=0.0)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)




    
    
#=================================================COMMENT DATABASE================================================




class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))


    
    
    
#=================================================SAVED DATABASE================================================
    
    
    

class SavedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref='saved_items')
    item = db.relationship('Item', backref='saved_by_users')





#=================================================HOME================================================



@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')



@app.route('/send_verification', methods=['GET', 'POST'])
def send_verification():
    if request.method == 'POST':
        email = request.form.get('Email')
        user = User.query.filter_by(email=email).first()
        rider = Rider_kyc.query.filter_by(email=email).first()

        if not user and not rider:
            flash('Email not registered!', 'danger')
            return redirect(url_for('register'))

        # Determine which user object to use
        account = user if user else rider
            
        if account.email_verified:
            flash('Email already verified!', 'info')
            return redirect(url_for('login'))

        token = secrets.token_urlsafe(16)
        # Store both email and account type for verification
        verification_tokens[token] = {'email': email, 'type': 'user' if user else 'rider'}
        
        verification_link = url_for('verify_email', token=token, _external=True)
        msg = Message('Verify Your Email', recipients=[email])
        msg.body = f'Click the link to verify your email: {verification_link}'
        
        try:
            mail.send(msg)
            flash('Verification email sent!', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')

        return redirect(url_for('send_verification'))

    return render_template('verify_email.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    token_data = verification_tokens.get(token)

    if token_data:
        email = token_data['email']
        account_type = token_data['type']
        
        if account_type == 'user':
            account = User.query.filter_by(email=email).first()
        else:  # rider
            account = Rider_kyc.query.filter_by(email=email).first()
            
        if account:
            account.email_verified = True
            db.session.commit()
            del verification_tokens[token]
            flash(f'Email {email} verified successfully!', 'success')

            # Role-based redirection
            if isinstance(account, User):
                if account.role == "vendor":
                    return redirect(url_for('additems'))
                elif account.role == "consumer":
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('dashboard'))  # Default for other roles
            elif isinstance(account, Rider_kyc):
                return redirect(url_for('profile'))  # Redirect riders to their profile page

    flash('Invalid or expired token!', 'danger')
    return redirect(url_for('home'))





#=================================================REGISTER================================================

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('Name')
        phone = request.form.get('Phone')
        email = request.form.get('Email')
        password = request.form.get('Password')
        role = request.form.get('Role')
        upi_id = request.form.get('UPI') if role == 'vendor' else None
        location= request.form.get('Location') if role == 'consumer' else None

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('login'))

        if role == 'vendor' and not upi_id:
            flash('UPI ID is required for vendors!', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, phone=phone, role=role, upi_id=upi_id, location=location)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
            
        email_sent = send_welcome_email(email, name, is_registration=True)
        if not email_sent:
            flash('Registration successful, but welcome email could not be sent.', 'warning')
        else:
            flash(f'Registration successful as {role}! Please check your email.', 'success')


        if role == 'consumer':
            return redirect(url_for('login'))
        elif role=='vendor':
            return redirect(url_for('login'))
        else:
            return redirect(url_for('rider_kyc'))
    return render_template('register.html')




#=================================================LOGIN================================================



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.email_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('send_verification'))

            # Store updated user data in session
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['user_photo'] = user.photo
            session.modified = True  # Ensure session refresh

            email_sent = send_welcome_email(user.email, user.name, is_registration=False)
            if not email_sent:
                flash('Login successful, but notification email could not be sent.', 'warning')
            else:
                flash(f'Login successful as {user.role}! Login notification sent to your email.', 'success')

            # Redirect based on role
            if user.role == "vendor":
                return redirect(url_for('additems'))
            elif user.role == "consumer":
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')






#=================================================LOGOUT================================================




@app.route('/logout')
def logout():
    if 'user_id' in session or 'rider_id' in session:
        session.clear()
        flash('Logged out successfully!', 'info')
        return redirect(url_for('login'))

    flash("You are not logged in!", "warning")
    return redirect(url_for('home'))





#=================================================TERMS&AGREEMENT================================================


@app.route('/terms', methods=['GET', 'POST'])
def terms():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please log in to accept the terms.", "warning")
            return redirect(url_for('login'))

        user = User.query.get(user_id)
        if user:
            user.terms_accepted = True
            db.session.commit()
            flash("You have successfully accepted the Terms & Conditions.", "success")
            return redirect(url_for('kyc'))

    return render_template('terms.html')





#=================================================KYC================================================

    
UPLOAD_FOLDER = 'static/UserInfo'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/kyc', methods=['GET', 'POST'])
def kyc():
    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        phone = request.form.get('Phone')
        id_number = request.form.get('Id_number')
        id_proof = request.files.get('Id_proof')
        photo_path = request.files.get('Photo')

        existing_vendor = Vendor_kyc.query.filter_by(email=email).first()
        if existing_vendor:
            flash("This email is already registered. Please log in or use a different email.", "danger")
            return redirect(url_for('kyc'))

        if not all([id_proof]):
            flash("All KYC documents are required!", "danger")
            return redirect(url_for('kyc'))
        id_proof_path = save_file(id_proof)
        
        if not all([photo_path]):
            flash("All KYC documents are required!", "danger")
            return redirect(url_for('kyc'))
        id_proof_path = save_file(photo_path)
        
        new_vendor = Vendor_kyc(
            name=name,
            email=email,
            phone=phone,
            id_number=id_number,
            role="vendor",
            id_proof=id_proof_path,
            photo_path = photo_path
        )

        db.session.add(new_vendor)
        db.session.commit()

        flash(f'KYC submitted successfully for {new_vendor.name}!', "success")
        return redirect(url_for('profile'))

    return render_template('kyc.html')




@app.route('/business', methods=['GET', 'POST'])
def business_details():
    if 'user_id' not in session or session.get('user_role') != "vendor":
        flash("Only verified vendors can submit business details.", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get(session['user_id'])

    if not user.email_verified:
        flash("You must verify your email before submitting business details.", "warning")
        return redirect(url_for('send_verification'))

    if request.method == "POST":
        business_name = request.form.get('Business_name')
        address = request.form.get('Address')
        latitude = request.form.get('Latitude')
        longitude = request.form.get('Longitude')

        if not latitude or not longitude:
            flash('Please get your location before submitting.', 'danger')
            return redirect(url_for('business_details'))

        existing_business = User.query.filter_by(business_name=business_name).first()
        if existing_business and existing_business.id != user.id:
            flash('This business name is already registered!', 'danger')
            return redirect(url_for('business_details'))

        user.business_name = business_name
        user.address = address
        user.latitude = latitude
        user.longitude = longitude
        db.session.commit()

        flash(f'Business "{business_name}" registered successfully with location!', 'success')
        return redirect(url_for('additems'))

    return render_template('business_details.html', user=user)


    
#=================================================ADDITEMS================================================




@app.route('/additems', methods=['GET', 'POST'])
def additems():
    if 'user_id' not in session or session.get('user_role') != "vendor":
        flash("You must be a vendor to access this page.", "danger")
        return redirect(url_for('dashboard'))
    user = User.query.get(session['user_id'])

    if not user.email_verified:
        flash('You must verify your email before adding items.', 'danger')
        return redirect(url_for('dashboard'))

    if not user.terms_accepted:
        flash('You must accept the Terms & Conditions before adding items.', 'danger')
        return redirect(url_for('dashboard'))

    user_id = session['user_id']

    if request.method == 'POST':
        itemId = request.form["Item_id"]
        name = request.form["Item_name"]
        context = request.form["Context"]
        image = request.files["Image"]
        amount= request.form["Amount"]
        stock = int(request.form["Stock"])
        region= request.form['Region']
        categories = request.form['Categories']
        type= request.form['Type']
        


        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER_ITEM'], image.filename)
            image.save(image_path)
            image_url = f"uploads/{image.filename}"
        else:
            image_url = None

        new_item = Item(itemid=itemId, name=name, context=context, image_url=image_url,stock=stock, amount=amount, user_id=user_id, region=region, type=type, categories=categories)
        db.session.add(new_item)
        db.session.commit()

    items = Item.query.filter_by(user_id=user_id).all()
    return render_template('additems.html', items=items)

                    #====UPDATE ITEMS=====

@app.route('/update_item/<int:item_id>', methods=['POST'])
def update_item(item_id):
    if 'user_id' not in session:
        flash('You must be logged in to update items.', 'danger')
        return redirect(url_for('login'))

    item = Item.query.get_or_404(item_id)

    if session['user_id'] != item.user_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('additems'))

    new_name = request.form.get('new_name', '').strip()
    new_context = request.form.get('new_context', '').strip()
    new_amount = request.form.get('new_amount', '').strip()
    new_stock = request.form.get('new_stock', '').strip()

    if new_name:
        item.name = new_name
    if new_context:
        item.context = new_context
    if new_amount:
        try:
            item.amount = float(new_amount)
        except ValueError:
            flash("Invalid amount. Please enter a valid number.", "danger")
            return redirect(url_for('additems'))
    if new_stock:
        try:
            item.stock = float(new_stock)
        except ValueError:
            flash("Invalid amount. Please enter a valid number.", "danger")
            return redirect(url_for('additems'))

    db.session.commit()
    flash('Item updated successfully!', 'success')
    return redirect(url_for('additems'))



                    #====UPDATE ITEMS=====


@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'user_id' not in session:
        flash('You must be logged in to delete items.', 'danger')
        return redirect(url_for('login'))

    item = Item.query.get_or_404(item_id)

    if session['user_id'] != item.user_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('additems'))

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('additems'))

                    #====STOCK=====


@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase_item(item_id):
    item = Item.query.get_or_404(item_id)

    if item.stock > 0:
        item.stock -= 1
        db.session.commit()
        flash("Purchase successful!", "success")
    else:
        flash("Out of stock!", "danger")

    return redirect(url_for('home'))






#=================================================DASHBOARD================================================



@app.route('/dashboard')
def dashboard():
    search_query = request.args.get('search', '').strip()
    selected_region = request.args.get('region', '').strip()
    query = Item.query.join(User)
    if search_query:
        query = query.filter(
            (Item.name.ilike(f"%{search_query}%")) |
            (Item.context.ilike(f"%{search_query}%")) |
            (User.name.ilike(f"%{search_query}%"))
        )
    if selected_region:
        if selected_region == "Others":
            query = query.filter(or_(Item.region.is_(None), Item.region == ""))
        else:
            query = query.filter(Item.region == selected_region)
    items = query.all()
    popular_items = Item.query.order_by(Item.order_count.desc()).limit(5).all()
    categories = ["Breakfast", "Lunch", "Dinner", "Desserts", "Drinks"]
    categorized_items = {
        category: Item.query.filter(Item.categories == category).order_by(Item.order_count.desc()).limit(5).all()
        for category in categories
    }
    users = User.query.filter_by(role='vendor').all()
    unique_regions = db.session.query(Item.region).distinct().all()
    unique_regions = [r[0] for r in unique_regions if r[0]]

    return render_template(
        'dashboard.html',
        items=items,
        users=users,
        popular_items=popular_items,
        categorized_items=categorized_items,
        unique_regions=unique_regions,
        search_query=search_query,
        selected_region=selected_region
    )


#=================================================VENDOR DETAIL PAGE================================================



@app.route('/vendor/<int:vendor_id>')
def vendor_details(vendor_id):
    vendor = User.query.filter_by(id=vendor_id, role='vendor').first()
    if not vendor:
        flash("Vendor not found!", "danger")
        return redirect(url_for('dashboard'))
    
    items = Item.query.filter_by(user_id=vendor.id).all()
    return render_template('vendor_details.html', vendor=vendor, items=items)





#=================================================ITEM DETAILS PAGE================================================



@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item_details(item_id):
    item = Item.query.get_or_404(item_id)
    comments = Comment.query.filter_by(item_id=item.id).all()

    if request.method == 'POST':
        if 'user_email' in session:
            quantity = int(request.form.get('quantity', 1))
            if quantity > item.stock:
                flash('Not enough stock available!', 'danger')
            else:
                item.stock -= quantity
                db.session.commit()
                flash('Item added to order!', 'success')
                return redirect(url_for('place_order', item_name=item.name, amount=item.amount * quantity, seller_email=item.seller.email))
        else:
            flash('Please log in to place an order.', 'danger')
            return redirect(url_for('login'))

    return render_template('item_details.html', item=item, comments=comments)



#=================================================LIKE/DISLIKE ITEM================================================



@app.route('/like_item/<int:item_id>', methods=['POST'])
def like_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.likes += 1
    db.session.commit()
    return redirect(url_for('item_details', item_id=item_id))

@app.route('/dislike_item/<int:item_id>', methods=['POST'])
def dislike_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.dislikes += 1
    db.session.commit()
    return redirect(url_for('item_details', item_id=item_id))



#=================================================COMMENT ON ITEM================================================



@app.route('/comment/<int:item_id>', methods=['POST'])
def comment_item(item_id):
    if 'user_email' not in session:
        flash('Please log in to comment.', 'danger')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    text = request.form.get('comment')
    if text:
        new_comment = Comment(item_id=item_id, user_id=user.id, text=text)  # Store user_id
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!', 'success')

    return redirect(url_for('item_details', item_id=item_id))




#=================================================SAVE ITEM FOR LATER================================================



@app.route('/save_item/<int:item_id>', methods=['POST'])
def save_item(item_id):
    if 'user_email' not in session:
        flash('Please log in to save items.', 'danger')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session['user_email']).first()
    
    existing_saved = SavedItem.query.filter_by(user_id=user.id, item_id=item_id).first()
    if existing_saved:
        flash('Item already saved!', 'info')
        return redirect(url_for('dashboard'))

    saved_item = SavedItem(user_id=user.id, item_id=item_id)
    db.session.add(saved_item)
    db.session.commit()

    flash('Item saved for later!', 'success')
    return redirect(url_for('dashboard'))



#=================================================UPDATE STOCK================================================


@app.route('/update_stock/<int:item_id>', methods=['POST'])
def update_stock(item_id):
    if 'user_id' not in session or session.get('user_role') != "vendor":
        flash("You must be a vendor to update stock.", "danger")
        return redirect(url_for('dashboard'))

    item = Item.query.get_or_404(item_id)
    new_stock = request.form.get('new_stock')

    if new_stock.isdigit():
        item.stock = int(new_stock)
        db.session.commit()
        flash('Stock updated successfully!', 'success')
    else:
        flash('Invalid stock value.', 'danger')

    return redirect(url_for('additems'))



#=================================================PLACE ORDER================================================


    

@app.route('/place_order/<int:item_id>', methods=['POST'])
def place_order(item_id):
    if "user_email" not in session or session.get("user_role") != "consumer":
        flash("Only consumers can place orders.", "danger")
        return redirect(url_for("dashboard"))

    item = Item.query.get(item_id)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("dashboard"))

    try:
        quantity = int(request.form.get("quantity", 0))
        item_name = request.form.get("item_name")
        amount = request.form.get("amount")
        seller_email = request.form.get("seller_email")

        amount = float(amount) if amount else None

        if not item_name or amount is None or not seller_email:
            flash("Invalid order data. Please try again.", "danger")
            return redirect(url_for("item_details", item_id=item.id))

        if quantity < 1:
            flash("Please enter a valid quantity.", "danger")
            return redirect(url_for("item_details", item_id=item.id))

        if quantity > item.stock:
            flash("Not enough stock available!", "danger")
            return redirect(url_for("item_details", item_id=item.id))

    except ValueError:
        flash("Invalid input. Please enter a valid quantity.", "danger")
        return redirect(url_for("item_details", item_id=item.id))

    seller = User.query.filter_by(email=seller_email).first()
    if not seller or not seller.upi_id:
        flash("Seller has not set up UPI payments.", "danger")
        return redirect(url_for("dashboard"))
    
    consumer = User.query.filter_by(email=session['user_email']).first()
    if not consumer:
        flash("Consumer account not found.", "danger")
        return redirect(url_for("dashboard"))

    order_id = str(uuid.uuid4())[:12]
    total_amount = round(amount * quantity, 2)

    upi_link = (
        f"upi://pay?pa={urllib.parse.quote(seller.upi_id)}"
        f"&pn={urllib.parse.quote(seller.name)}"
        f"&tid={order_id}"
        f"&tr={order_id}"
        f"&tn={urllib.parse.quote(f'Payment for Order #{order_id}')}"
        f"&am={format(total_amount, '.2f')}"
        f"&cu=INR"
    )    
    estimated_delivery = datetime.datetime.utcnow() + timedelta(minutes=30)

    new_order = Order(
        id=order_id,
        item_name=item_name,
        user_email=session['user_email'],
        amount=total_amount,
        quantity=quantity,
        upi_link=upi_link,
        consumer_id=consumer.id,  
        vendor_id=seller.id      
    )
    
    db.session.add(new_order)
    item.stock -= quantity

    # ✅ Initialize `order_count` before using it
    order_count = Order.query.count()  # Fetch total order count
    order_count += 1

    db.session.commit()

    flash('Order placed successfully! Complete payment to confirm.', 'info')
    return redirect(url_for('payment_page', order_id=order_id))





#=================================================PAYMENT PAGE================================================




@app.route('/payment/<order_id>')
def payment_page(order_id):
    order= Order.query.get_or_404(order_id)
    return render_template('payment.html', order=order)



#=================================================GENERATE QR================================================
            
@app.route('/generate_upi/<int:order_id>', methods=['GET'])
def generate_upi(order_id):
    order = db.session.query(Order).filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    total_amount = order.total_amount
    vendor = db.session.query(User).filter_by(id=order.vendor_id).first()

    upi_link = (
        f"upi://pay?pa={vendor.email}&pn={vendor.name}&am={total_amount}&cu=INR"
    )

    # Generate QR Code for UPI Payment
    qr = qrcode.make(upi_link)
    qr_path = f'static/qr_{order_id}.png'
    qr.save(qr_path)

    return jsonify({
        "upi_link": upi_link,
        "qr_code_url": qr_path
    })        
    
    



@app.route('/qr/<order_id>')
def generate_qr(order_id):
    order = Order.query.get_or_404(order_id)
    
    qr_dir = 'static/QrCode'
    os.makedirs(qr_dir, exist_ok=True)
    
    qr = qrcode.QRCode(
        version=1,               
        error_correction=qrcode.constants.ERROR_CORRECT_L,  
        box_size=10,             
        border=4                  
    )
    qr.add_data(order.upi_link)
    qr.make(fit=True)

    qr_path = f'{qr_dir}/qr_{order_id}_{int(time.time())}.png'
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img.save(qr_path)

    return send_file(qr_path, mimetype='image/png', as_attachment=False)



            #====CLEAN-UP PRE-EXISTING QR CODES=====


def cleanup_qr_code(qr_path):
    try:
        if os.path.exists(qr_path):
            os.remove(qr_path)
    except Exception as e:
        print(f"Error cleaning up QR code: {str(e)}")
    
    
    
#=================================================CONFIRM PAYMENT================================================    

    
    
@app.route("/confirm_payment/<order_id>", methods=["POST"])
def confirm_payment(order_id):
    order = Order.query.get_or_404(order_id)
    order.payment_status = "Paid"
    db.session.commit()
    flash("Payment confirmed! Your order will be processed soon.", "success")
    return redirect(url_for("my_orders"))



#=================================================CANCEL ORDER================================================



@app.route('/cancel_order/<order_id>', methods=['POST'])
def cancel_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("dashboard"))

    if order.status != "pending":
        flash("This order cannot be cancelled.", "warning")
        return redirect(url_for("dashboard"))

    item = Item.query.filter_by(name=order.item_name).first()
    if item:
        item.stock += order.quantity

    order.status = "cancelled"
    db.session.commit()

    seller = User.query.filter_by(email=order.user_email).first()
    
    if seller:
        send_cancellation_email(seller.email, order)

    flash("Order has been cancelled successfully. The vendor has been notified.", "success")
    return redirect(url_for("dashboard"))


            #=========SEND CANCELLATION EMAIL=========
            

def send_cancellation_email(vendor_email, order):
    subject = "Order Cancellation Notification"
    body = f"""
    Hello,

    The following order has been cancelled:

    - Order ID: {order.id}
    - Item: {order.item_name}
    - Quantity: {order.quantity}
    - Amount: ₹{order.amount}
    - Cancelled at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

    Please update your records accordingly.

    Regards,
    HomeKitchen Team
    """

    msg = Message(subject=subject, recipients=[vendor_email], body=body)
    
    try:
        mail.send(msg)
        print("Cancellation email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")



#======================================================WALLET====================================================


@app.route('/wallet', methods=['GET'])
def wallet_dashboard():
    if 'rider_id' in session:  # ✅ Prioritize rider_id if present
        rider = db.session.get(Rider_kyc, session['rider_id'])
        if not rider:
            flash('Rider account not found.', 'danger')
            return redirect(url_for('logout'))

        transactions = Transaction.query.filter_by(rider_id=rider.id).all()
        wallet_balance = rider.wallet_balance

        return render_template(
            'wallet.html',
            user=None,  # Rider does not need user data
            rider=rider,
            transactions=transactions,
            wallet_balance=wallet_balance
        )

    elif 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if not user:
            flash('User account not found.', 'danger')
            return redirect(url_for('logout'))

        transactions = []
        if user.role == 'vendor':
            transactions = Transaction.query.filter_by(vendor_id=user.id).all()
        elif user.role == 'consumer':
            transactions = Transaction.query.filter_by(consumer_id=user.id).all()

        wallet_balance = user.wallet_balance

        return render_template(
            'wallet.html',
            user=user,
            rider=None,  # User does not need rider data
            transactions=transactions,
            wallet_balance=wallet_balance
        )

    flash('Please log in to access your wallet.', 'danger')
    return redirect(url_for('login'))


# =================== WALLET BALANCE API ======================



@app.route('/api/wallet/<int:user_id>', methods=['GET'])
def wallet_api(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    rider = db.session.query(Rider_kyc).filter_by(id=user_id).first()

    if not user and not rider:
        return jsonify({"error": "User or Rider not found"}), 404

    if user:
        wallet_balance = user.wallet_balance
        transactions = (
            Transaction.query.filter_by(vendor_id=user.id).all()
            if user.role == 'vendor' else
            Transaction.query.filter_by(consumer_id=user.id).all()
        )
    else:  # Rider case
        wallet_balance = rider.wallet_balance
        transactions = Transaction.query.filter_by(rider_id=rider.id).all()

    return jsonify({
        "wallet_balance": wallet_balance,
        "transactions": [
            {
                "order_id": t.order_id,
                "vendor_share": t.vendor_share,
                "rider_share": t.rider_share,
                "platform_share": t.platform_share,
                "timestamp": t.timestamp
            }
            for t in transactions
        ]
    })




#=================================================MY ORDERS================================================



@app.route("/my_orders")
def my_orders():
    if "user_email" not in session:
        flash("Please log in to view your orders.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    
    # Get orders with vendor information
    orders_list = []
    raw_orders = Order.query.filter_by(user_email=user_email).order_by(Order.created_at.desc()).all()
    
    for order in raw_orders:
        # Get vendor information
        vendor = User.query.get(order.vendor_id)
        
        # Try to find an item with the same name to get its image
        item = Item.query.filter_by(name=order.item_name).first()
        
        # Default image if no item found
        image_url = "images/default-food.jpg"
        if item:
            image_url = item.image_url
            
        # Create order data dictionary
        order_data = {
            'id': order.id,
            'item_name': order.item_name,
            'amount': order.amount,
            'status': order.status,
            'created_at': order.created_at,
            'upi_link': order.upi_link,
            'image_url': image_url,
            'vendor_name': vendor.name if vendor else "Unknown Vendor",
            'shop_name': vendor.business_name if vendor and vendor.business_name else "Home Kitchen"
        }
        
        orders_list.append(order_data)

    return render_template("my_orders.html", orders=orders_list)


#=================================================WELCOME MAIL================================================



def send_welcome_email(user_email, user_name, is_registration=True):

    try:
        if is_registration:
            subject = "Welcome to Our Marketplace!"
            body = f"""
Dear {user_name},

Welcome to our marketplace! We're thrilled to have you join our community.

Your account has been successfully created. You can now:
- Browse items from various vendors
- Place orders
- Track your purchases
- {'Manage your store and list items' if session.get('user_role') == 'vendor' else 'Shop from our trusted vendors'}

If you have any questions, feel free to reach out to our support team.

Best regards,
Your HomeKitchen Team
            """
        else:
            subject = "New Login Detected"
            body = f"""
Dear {user_name},

We detected a new login to your account.

Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If this wasn't you, please contact our support team immediately.

Best regards,
Your HomeKitchen Team
            """

        msg = Message(
            subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email notification error: {str(e)}")
        return False



#=================================================ORDER NOTIFICATION MAIL================================================


    
    
def send_order_notifications(order_id, item_name, amount, seller_email, quantity):
    seller = User.query.filter_by(email=seller_email).first()
    if not seller:
        return False

    try:
        email_msg = Message('New Order Received!', sender=app.config['MAIL_USERNAME'], recipients=[seller.email])
        email_msg.body = f"""
Hello {seller.name},

You have received a new order!

Order Details:
- Order ID: {order_id}
- Item: {item_name}
- Amount: ₹{amount}
-Quantity: {quantity}

Please check your dashboard for more details.

Best regards,
Your HomeKitchen Team
        """
        mail.send(email_msg)

        sms_message = f"New order received! Order ID: {order_id}, Item: {item_name}, Amount: ₹{amount}"

        return True
    except Exception as e:
        print(f"Notification error: {str(e)}")
        return False    

    
    

#=================================================PROFILE================================================


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('logout'))

    now = datetime.datetime.utcnow()

    if request.method == 'POST':
        try:
            user.name = request.form.get('name')
            user.phone = request.form.get('phone')
            
            user.latitude = request.form.get('latitude')
            user.longitude = request.form.get('longitude')

            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Handle password change
            if current_password and new_password and confirm_password:
                if not user.check_password(current_password):
                    flash('Current password is incorrect.', 'danger')
                    return redirect(url_for('profile'))

                if new_password != confirm_password:
                    flash('New passwords do not match.', 'danger')
                    return redirect(url_for('profile'))

                user.set_password(new_password)

            # Handle profile image upload
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    user.photo = f'images/{filename}'

            # Handle UPI ID update for vendors
            if user.role == 'vendor':
                user.upi_id = request.form.get('upi_id')

            # Save to database
            db.session.commit()

            # Update session data to reflect changes immediately
            session['user_name'] = user.name
            session['user_photo'] = user.photo
            session.modified = True

            flash('Profile updated successfully!', 'success')

            # Send email notification
            msg = Message(
                'Profile Update Notification',
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]
            )
            msg.body = f"""
Hello {user.name},

Your profile was recently updated. If you did not make these changes, please contact support immediately.

Time of update: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC

Best regards,
Your HomeKitchen Team
            """
            mail.send(msg)

            return redirect(url_for('profile'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
            print(f"Profile update error: {str(e)}")

    return render_template('profile.html', user=user)
    


#====================================================RIDER PROFILE========================================================



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/rider_profile', methods=['GET', 'POST'])
def rider_profile():
    if 'rider_id' not in session:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('rider_login'))

    rider = db.session.get(Rider_kyc, session['rider_id'])

    if not rider:
        flash('Rider not found.', 'danger')
        return redirect(url_for('logout'))

    now = datetime.datetime.utcnow()

    if request.method == 'POST':
        try:
            rider.name = request.form.get('name')
            rider.phone = request.form.get('phone')

            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if current_password and new_password and confirm_password:
                if not rider.check_password(current_password):
                    flash('Current password is incorrect.', 'danger')
                    return redirect(url_for('rider_profile'))

                if new_password != confirm_password:
                    flash('New passwords do not match.', 'danger')
                    return redirect(url_for('rider_profile'))

                rider.set_password(new_password)

            # Handle profile image upload
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    rider.photo = f'images/{filename}'

            db.session.commit()

            # Update session variables
            session['rider_name'] = rider.name
            session['rider_photo'] = rider.photo
            session.modified = True

            flash('Profile updated successfully!', 'success')

            msg = Message(
                'Profile Update Notification',
                sender=app.config['MAIL_USERNAME'],
                recipients=[rider.email]
            )
            msg.body = f"""
Hello {rider.name},

Your profile was recently updated. If you did not make these changes, please contact support immediately.

Time of update: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC

Best regards,
Your HomeKitchen Team
            """
            mail.send(msg)

            return redirect(url_for('rider_profile'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
            print(f"Profile update error: {str(e)}")

    total_deliveries = 0
    monthly_earnings = 0
    weekly_earnings = 0

    if rider.role == 'rider':
        total_deliveries = Order.query.filter_by(rider_id=rider.id, status='delivered').count()

        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

        monthly_earnings = db.session.query(func.sum(Order.rider_fee)).filter(
            Order.rider_id == rider.id,
            Order.status == 'delivered',
            Order.delivered_at.isnot(None),  # Ensure delivered_at is not NULL
            Order.delivered_at >= first_day_of_month,
            Order.delivered_at < now
        ).scalar() or 0

        weekly_earnings = db.session.query(func.sum(Order.rider_fee)).filter(
            Order.rider_id == rider.id,
            Order.status == 'delivered',
            Order.delivered_at.isnot(None),  # Ensure delivered_at is not NULL
            Order.delivered_at >= start_of_week,
        ).scalar() or 0

    return render_template(
        'rider_profile.html',
        rider=rider,
        total_deliveries=total_deliveries,
        monthly_earnings=monthly_earnings,
        weekly_earnings=weekly_earnings
    )    
    

#====================================================DELETE ACCOUNT================================================



@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('profile'))

    try:
        Order.query.filter_by(consumer_id=user.id).delete()
        Order.query.filter_by(vendor_id=user.id).delete()
        Order.query.filter_by(rider_id=user.id).delete()

        db.session.delete(user)
        db.session.commit()

        session.clear()
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('home'))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting your account.', 'danger')
        print(f"Error deleting account: {str(e)}")

    return redirect(url_for('profile'))



#====================================================RIDER KYC================================================




@app.route('/rider_kyc', methods=['GET', 'POST'])
def rider_kyc():
    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        phone = request.form.get('Phone')
        password = request.form.get('Password')
        vehicle_type= request.form.get('Vehicle_type')
        vehicle_number= request.form.get('Vehicle_number')

        if not all([name, email, phone, password]):
            flash("All fields are required!", "danger")
            return redirect(url_for('rider_kyc'))

        existing_rider = Rider_kyc.query.filter_by(email=email).first()
        if existing_rider:
            flash("This email is already registered. Please log in or use a different email.", "danger")
            return redirect(url_for('rider_kyc'))

        id_proof = request.files.get('Id_proof')
        license = request.files.get('License')
        insurance = request.files.get('Insurance')
        photo = request.files.get('Photo')

        if not all([id_proof, license, insurance, photo]):
            flash("All KYC documents are required!", "danger")
            return redirect(url_for('rider_kyc'))

        id_proof_path = save_file(id_proof)
        license_path = save_file(license)
        insurance_path = save_file(insurance)
        photo_path = save_file(photo)

        new_rider = Rider_kyc(
            name=name,
            email=email,
            phone=phone,
            role="rider",
            vehicle_type= vehicle_type,
            vehicle_number= vehicle_number,
            id_proof=id_proof_path,
            license=license_path,
            insurance=insurance_path,
            photo=photo_path,
            verified=False
        )
        new_rider.set_password(password)

        db.session.add(new_rider)
        db.session.commit()

        flash(f'KYC submitted successfully for {new_rider.name}!', "success")
        return redirect(url_for('rider_profile'))

    return render_template('rider_kyc.html')


def save_file(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename
    return None



#=================================================RIDER LOGIN========================================================= 



@app.route('/rider_login', methods=['GET', 'POST'])
def rider_login():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        rider = Rider_kyc.query.filter_by(email=email).first()

        if rider and rider.check_password(password):
            if not rider.email_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('send_verification'))

            session['rider_id'] = rider.id
            session['rider_role'] = 'rider'
            session['rider_email'] = rider.email
            session['rider_name'] = rider.name
            session['rider_photo'] = rider.photo
            session.modified = True

            email_sent = send_welcome_email(rider.email, rider.name, is_registration=False)
            if not email_sent:
                flash('Login successful, but notification email could not be sent.', 'warning')
            else:
                flash('Login successful as rider! Login notification sent to your email.', 'success')

            return redirect(url_for('rider_profile'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('rider_login'))

    return render_template('rider_login.html')



#========================================================ADMIN==========================================================



@app.route('/verify_users', methods=['GET', 'POST'])
def verify_users():
    vendors = Vendor_kyc.query.filter_by(role="vendor", verified=False).all()
    riders = Rider_kyc.query.filter_by(role="rider", verified=False).all()

    riders_data = [
        {
            'id': rider.id,
            'name': rider.name,
            'email': rider.email,
            'phone': rider.phone,
            'id_proof_url': f"static/UserInfo/{rider.id_proof}" if rider.id_proof else "",
            'license_url': f"static/UserInfo/{rider.license}" if rider.license else "",
            'insurance_url': f"static/UserInfo/{rider.insurance}" if rider.insurance else "",
            'photo_url': f"static/UserInfo/{rider.photo}" if rider.photo else ""
        }
        for rider in riders
    ]

    vendors_data = [
        {
            'id': vendor.id,
            'name': vendor.name,
            'email': vendor.email,
            'phone': vendor.phone,
            'business_name': vendor.business_name,
            'id_proof_url': f"static/UserInfo/{vendor.id_proof}" if vendor.id_proof else "",
            'photo_url': f"static/UserInfo/{vendor.photo_path}" if vendor.photo_path else ""
        }
        for vendor in vendors
    ]

    return render_template('verify_users.html', riders=riders_data, vendors=vendors_data)



@app.route('/verify_rider/<int:rider_id>', methods=['POST'])
def verify_rider(rider_id):
    rider = Rider_kyc.query.get(rider_id)
    if not rider:
        return jsonify({'error': 'Rider not found'}), 404

    rider.verified = True
    db.session.commit()
    return jsonify({'message': f'Rider {rider.name} verified successfully!'}), 200


@app.route('/verify_vendor/<int:vendor_id>', methods=['POST'])
def verify_vendor(vendor_id):
    vendor = Vendor_kyc.query.filter_by(id=vendor_id, role='vendor').first()
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404

    vendor.verified = True
    db.session.commit()
    return jsonify({'message': f'Vendor {vendor.name} verified successfully!'}), 200



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form.get('Name')
        password= request.form.get('Password')
        
        if name == 'Rajan' and password == 'Redrajen@083':
            flash('Admin logged in successfully!', 'success')
            return redirect(url_for('verify_users'))
        else:
            flash('Unauthoriized login', 'danger')
            return redirect(url_for('home'))
    return render_template('admin_login.html')



    
#=================================================ASSIGN ORDERS========================================================= 
    
    
        
@app.route('/assign_order', methods=['GET', 'POST'])
def assign_order():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        rider_id = request.form.get('rider_id')
        
        order = db.session.get(Order, order_id)
        rider= db.session.get(Rider_kyc, rider_id)
        
        if not order:
            flash("Order not found!", "danger")
            return redirect(url_for('assign_order'))
        if not rider or rider.role != 'rider':
            flash("Invalid rider selected!", "danger")
            return redirect(url_for('assign_order'))
        
        order.rider_id = rider_id
        order.status = "Assigned to Rider"
        db.session.commit()
        
        flash(f"Order {order.id} has been assigned to {rider.name}!", "success")
        return redirect(url_for('additems'))

    else:
        orders = Order.query.filter(Order.rider_id == None).all()
        riders = Rider_kyc.query.filter_by(role='rider').all()
        return render_template('assign_order.html', orders=orders, riders=riders)




#=================================================RIDERS ORDERS========================================================= 





@app.route('/rider_orders/<int:rider_id>', methods=['GET'])
def rider_orders(rider_id):
    orders = Order.query.filter_by(rider_id=rider_id).all()
    
    order_list = []
    for order in orders:
        consumer = db.session.get(User, order.consumer_id) if order.consumer_id else None
        consumer_details = None
        if consumer:
            consumer_details = {
                "name": consumer.name,
                "phone": consumer.phone,
                "location": consumer.address,
                "email": consumer.email
            }
        
        vendor = db.session.get(User, order.vendor_id) if order.vendor_id else None
        vendor_details = None
        if vendor:
            vendor_details = {
                "name": vendor.name,
                "phone": vendor.phone,
                "location": vendor.address,
                "email": vendor.email
            }
        
        order_data = {
            "id": order.id,
            "item_name": order.item_name,
            "quantity": order.quantity,
            "amount": order.amount,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "consumer": consumer_details,
            "vendor": vendor_details
        }
        
        order_list.append(order_data)
    
    return render_template('rider_orders.html', orders=order_list, rider_id=rider_id)



#=====================================================UPDATE ORDER STATUS=====================================================

# Change Decimal values to floats
RIDER_COMMISSION_RATE = 0.10
PLATFORM_COMMISSION_RATE = 0.10
ADMIN_UPI_ID = '6283060669@ptsbi'

@app.route('/update_order_status/<string:order_id>/<string:status>', methods=['POST'])
def update_order_status(order_id, status):
    if "rider_id" not in session:
        flash("Only assigned riders can update order status.", "danger")
        return redirect(url_for("rider_profile"))
    # Fetch the order from the database
    order = db.session.get(Order, order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("rider_profile"))
    # Ensure the logged-in rider is assigned to this order
    if order.rider_id != session["rider_id"]:
        flash("You are not assigned to this order.", "danger")
        return redirect(url_for("rider_profile"))
    # Update order status
    if status.lower() == "in-transit":
        order.status = "in-transit"
        flash("Order marked as In Transit.", "success")
    elif status.lower() == "delivered":
        if order.payment_status == "Completed":
            flash("This order has already been marked as Delivered.", "info")
            return redirect(url_for("rider_orders", rider_id=session["rider_id"]))
        
        # Convert total_amount to float if it's a Decimal
        total_amount = float(order.amount) if hasattr(order.amount, 'quantize') else order.amount
        
        # Calculate shares using float values
        rider_share = total_amount * RIDER_COMMISSION_RATE
        platform_share = total_amount * PLATFORM_COMMISSION_RATE
        vendor_share = total_amount - (rider_share + platform_share)
        
        # Update Wallet Balances
        if order.vendor_id:
            vendor = db.session.get(User, order.vendor_id)
            if vendor:
                vendor.wallet_balance += vendor_share
        
        if order.rider_id:
            rider = db.session.get(Rider_kyc, order.rider_id)
            if rider:
                rider.wallet_balance += rider_share
        
        # Add platform share automatically to admin wallet
        # Assuming you have an Admin model or a specific admin user
        admin = db.session.get(User, 1)  # Replace with how you identify the admin user
        if admin:
            admin.wallet_balance += platform_share
        
        # Create Transaction Record
        transaction_id = str(uuid.uuid4())
        new_transaction = Transaction(
            order_id=order.id,
            amount=total_amount,
            transaction_id=transaction_id,
            vendor_share=vendor_share,
            rider_share=rider_share,
            platform_share=platform_share
        )
        
        # Mark Order as Completed
        order.status = "delivered"
        order.delivered_at = datetime.datetime.utcnow()
        order.payment_status = "Completed"
        
        # Save Changes
        db.session.add(new_transaction)
        db.session.commit()
        
        flash("Order marked as Delivered. Payment has been distributed.", "success")
        return redirect(url_for("rider_orders", rider_id=session["rider_id"]))
    else:
        flash("Invalid status update.", "danger")
    
    db.session.commit()
    return redirect(url_for("rider_orders", rider_id=session["rider_id"]))



#=================================================ADD MONEY TO WALLET================================================



@app.route('/add_money', methods=['GET', 'POST'])
def add_money():
    if 'user_id' not in session:
        flash('Please log in to add money to your wallet.', 'danger')
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        amount_str = request.form.get('amount')

        # Validate amount input
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Please enter a valid amount.', 'danger')
            return redirect(url_for('add_money'))

        upi_id = request.form.get('upi_id')
        if not upi_id:
            flash('Please enter your UPI ID.', 'danger')
            return redirect(url_for('add_money'))

        # Generate UPI payment link
        upi_link = f"upi://pay?pa={upi_id}&pn={user.name}&am={amount}&cu=INR"

        # Generate QR Code for UPI Payment
        qr = qrcode.make(upi_link)
        qr_path = f'static/qr_add_money_{user.id}.png'
        qr.save(qr_path)

        # ✅ FIX: Do not set order_id for wallet transactions
        transaction_id = str(uuid.uuid4())  # Unique transaction ID
        new_transaction = Transaction(
            order_id=None,  # ✅ No order associated with wallet top-ups
            vendor_id=user.id if user.role == "vendor" else None,
            consumer_id=user.id if user.role == "consumer" else None,
            rider_id=None,
            amount=amount,  # Positive for deposit
            transaction_id=transaction_id,
            vendor_share=0.0,
            rider_share=0.0,
            platform_share=0.0,
            timestamp=datetime.datetime.utcnow()
        )

        # Update Wallet Balance
        user.wallet_balance += amount
        db.session.add(new_transaction)
        db.session.commit()

        flash(f'₹{amount} added successfully to your wallet.', 'success')
        return render_template('add_money.html', upi_link=upi_link, qr_path=qr_path, user=user)

    return render_template('add_money.html', user=user)



    #=================================================WITHDRAW MONEY FROM WALLET================================================



@app.route('/withdraw_money', methods=['GET', 'POST'])
def withdraw_money():
    if 'user_id' not in session:
        flash('Please log in to withdraw money from your wallet.', 'danger')
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        amount_str = request.form.get('amount')
        
        # Validate input amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Please enter a valid withdrawal amount.', 'danger')
            return redirect(url_for('withdraw_money'))

        # Ensure sufficient balance
        if amount > user.wallet_balance:
            flash('Insufficient wallet balance.', 'danger')
            return redirect(url_for('withdraw_money'))

        upi_id = request.form.get('upi_id')
        if not upi_id:
            flash('Please enter your UPI ID.', 'danger')
            return redirect(url_for('withdraw_money'))

        # Deduct amount from wallet balance
        user.wallet_balance -= amount

        # Generate a unique withdrawal transaction ID
        transaction_id = str(uuid.uuid4())

        # Create a withdrawal transaction entry (without order_id)
        new_transaction = Transaction(
            order_id=None,  # ✅ No order associated with withdrawal
            vendor_id=user.id if user.role == "vendor" else None,
            consumer_id=user.id if user.role == "consumer" else None,
            rider_id=None,
            amount=-amount,  # Negative for withdrawal
            transaction_id=transaction_id,
            vendor_share=0.0,
            rider_share=0.0,
            platform_share=0.0,
            timestamp=datetime.datetime.utcnow()  # ✅ Add timestamp
        )

        db.session.add(new_transaction)
        db.session.commit()

        flash(f'₹{amount} withdrawn successfully. The amount will be credited to your UPI ID shortly.', 'success')
        return redirect(url_for('wallet_dashboard'))

    return render_template('withdraw_money.html', user=user)



    #=================================================COMPLETE ORDER================================================



@app.route('/complete_order/<string:order_id>', methods=['POST'])
def complete_order(order_id):
    if 'user_id' not in session:
        flash("Please log in to complete the order.", "danger")
        return redirect(url_for('login'))

    order = db.session.get(Order, order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('dashboard'))

    if order.status == "Completed":
        flash("This order has already been completed.", "warning")
        return redirect(url_for('dashboard'))

    vendor = db.session.get(User, order.vendor_id)
    consumer = db.session.get(User, order.consumer_id)
    rider = db.session.query(User).filter_by(role="rider").first()  # Get any available rider

    if not vendor or not consumer:
        flash("Vendor or Consumer details not found.", "danger")
        return redirect(url_for('dashboard'))

    # ✅ Calculate the split
    total_amount = order.amount
    vendor_share = round(total_amount * 0.75, 2)
    rider_share = round(total_amount * 0.10, 2)
    platform_share = round(total_amount * 0.15, 2)

    # ✅ Update Wallet Balances
    vendor.wallet_balance += vendor_share
    if rider:
        rider.wallet_balance += rider_share
    platform_wallet = db.session.query(User).filter_by(role="admin").first()  # Assuming an admin user
    if platform_wallet:
        platform_wallet.wallet_balance += platform_share

    # ✅ Add Transaction Entry
    transaction_id = str(uuid.uuid4())

    new_transaction = Transaction(
        order_id=order.id,
        vendor_id=vendor.id,
        consumer_id=consumer.id,
        rider_id=rider.id if rider else None,
        vendor_share=vendor_share,
        rider_share=rider_share,
        platform_share=platform_share,
        amount=total_amount,
        transaction_id=transaction_id,
        timestamp=datetime.datetime.utcnow()
    )

    # ✅ Mark Order as Completed
    order.status = "Completed"

    db.session.add(new_transaction)
    db.session.commit()

    flash("Order completed successfully! Payment has been processed.", "success")
    return redirect(url_for('wallet_dashboard'))




    #=================================================RUN================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)