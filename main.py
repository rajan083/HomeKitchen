from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from datetime import timedelta
from flask_mail import Mail, Message
from twilio.rest import Client
import uuid
import qrcode
import secrets
import urllib.parse
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key= 'SecretKey'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///user.db'
db=SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rm4952989@gmail.com'
app.config['MAIL_PASSWORD'] = 'qytf jjpo fxfa wlav'
app.config['MAIL_DEFAULT_SENDER'] = 'rm4952989@gmail.com'
mail = Mail(app)


TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


verification_tokens={}



#=================================================UPLOAD FOLDER================================================


    
UPLOAD_FOLDER_ITEM = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER_ITEM):
    os.makedirs(UPLOAD_FOLDER_ITEM)

app.config['UPLOAD_FOLDER_ITEM'] = UPLOAD_FOLDER_ITEM




#=================================================USER-DATABSE================================================



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable= False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    upi_id = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(10), nullable=False)
    items = db.relationship('Item', backref='seller')
    created_at= db.Column(db.DateTime, default= datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    business_name = db.Column(db.String(150), nullable=True, unique=True)
    terms_accepted = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)  
    latitude = db.Column(db.String(50), nullable=True)
    longitude = db.Column(db.String(50), nullable=True)



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



    

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


    

#=================================================ORDER================================================


    
class Order(db.Model):
    id= db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name= db.Column(db.String(100), nullable=False)
    user_email= db.Column(db.String(100), db.ForeignKey("user.email"), nullable=False)
    amount= db.Column(db.Float, nullable=False)
    upi_link= db.Column(db.String(500), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    payment_status= db.Column(db.String(20), default="Pending")
    status = db.Column(db.String(20), default="pending")  # ✅ Order status: pending, cancelled, delivered
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    
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

        if not user:
            flash('Email not registered!', 'danger')
            return redirect(url_for('register'))

        if user.email_verified:
            flash('Email already verified!', 'info')
            return redirect(url_for('login'))

        token = secrets.token_urlsafe(16)
        verification_tokens[token] = email
        
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
    email = verification_tokens.get(token)

    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_verified = True
            db.session.commit()
            del verification_tokens[token]
            flash(f'Email {email} verified successfully!', 'success')
            return redirect(url_for('login'))
    
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

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('login'))

        if role == 'vendor' and not upi_id:
            flash('UPI ID is required for vendors!', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, phone=phone, role=role, upi_id=upi_id)
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
        return redirect(url_for('terms'))

    return render_template('register.html')




#=================================================LOGIN================================================




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

        if not user.email_verified:
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('send_verification'))

        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_email'] = user.email

        email_sent = send_welcome_email(user.email, user.name, is_registration=False)
        if not email_sent:
            flash('Login successful, but notification email could not be sent.', 'warning')
        else:
            flash(f'Login successful as {user.role}! Login notification sent to your email.', 'success')

        if user.role == "vendor":
            return redirect(url_for('additems'))
        if user.role == "consumer":
            return redirect(url_for('dashboard'))

    return render_template('login.html')





#=================================================LOGOUT================================================




@app.route('/logout')
def logout():
    if 'user_id' in session:
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
        dob = request.form.get('Dob')
        email = request.form.get('Email')
        phone = request.form.get('Phone')
        id_number = request.form.get('Id_number')

        id_proof = request.files["Id_proof"]
        photo = request.files["Photo"]

        if id_proof and id_proof.filename and photo and photo.filename:
            id_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], id_proof.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)

            try:
                id_proof.save(id_proof_path)
                photo.save(photo_path)
                flash("KYC Submitted Successfully!", "success")
                return redirect(url_for('kyc'))
            except Exception as e:
                flash(f"Error saving files: {str(e)}", "danger")
                return redirect(url_for('kyc'))

        else:
            flash("Please upload required documents!", "danger")
            return redirect(url_for('kyc'))

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
        type= request.form['Type']
        


        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER_ITEM'], image.filename)
            image.save(image_path)
            image_url = f"uploads/{image.filename}"
        else:
            image_url = None

        new_item = Item(itemid=itemId, name=name, context=context, image_url=image_url,stock=stock, amount=amount, user_id=user_id, region=region, type=type)
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




from sqlalchemy import or_

@app.route('/dashboard', methods=['GET'])
def dashboard():
    search_query = request.args.get('search', '')
    selected_region = request.args.get('region', '')
    query = Item.query.join(User)
    if search_query:
        query = query.filter((Item.name.ilike(f"%{search_query}%")) | (Item.context.ilike(f"%{search_query}%")) | (User.name.ilike(f"%{search_query}%")))
    if selected_region:
        if selected_region == "Others":
            query = query.filter(or_(Item.region == None, Item.region == ""))
        else:
            query = query.filter(Item.region == selected_region)
    items = query.all()
    users = User.query.all()
    unique_regions = db.session.query(Item.region).distinct().all()
    unique_regions = [r[0] for r in unique_regions if r[0]]
    return render_template('dashboard.html', items=items, users=users, search_query=search_query, unique_regions=unique_regions, selected_region=selected_region)




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

    order_id = str(uuid.uuid4())[:12]
    total_amount = round(amount * quantity, 2)  # ✅ Fixed: Ensuring amount is rounded properly

    upi_link = f"upi://pay?pa={urllib.parse.quote(seller.upi_id)}&pn={urllib.parse.quote(seller.email)}&tid={order_id}&tr={order_id}&tn=OrderPayment&am={total_amount}&cu=INR"
    
    estimated_delivery = datetime.datetime.utcnow() + timedelta(minutes=30)  # ✅ Delivery in 30 minutes

    new_order = Order(
        id=order_id,
        item_name=item_name,
        user_email=session['user_email'],
        amount=total_amount,
        quantity=quantity,
        upi_link=upi_link
    )
    db.session.add(new_order)
    item.stock -= quantity
    db.session.commit()

    flash('Order placed successfully! Complete payment to confirm.', 'info')
    return redirect(url_for('payment_page', order_id=order_id))

                #========ORDER CONFIRMATION EMAIL========

def send_order_confirmation_email(consumer_email, order):
    subject = "Order Confirmation - HomeKitchen"
    body = f"""
    Hello,

    Your order has been successfully placed! Here are the details:

    - Order ID: {order.id}
    - Item: {order.item_name}
    - Quantity: {order.quantity}
    - Amount: ₹{order.amount}
    - Estimated Delivery: {order.estimated_delivery.strftime('%Y-%m-%d %H:%M:%S')} UTC

    Thank you for shopping with us!

    Regards,  
    HomeKitchen Team
    """

    msg = Message(subject=subject, recipients=[consumer_email], body=body)
    
    try:
        mail.send(msg)
        print("Order confirmation email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")





#=================================================PAYMENT PAGE================================================




@app.route('/payment/<order_id>')
def payment_page(order_id):
    order= Order.query.get_or_404(order_id)
    return render_template('payment.html', order=order)



#=================================================GENERATE QR================================================


            #====CLEAN-UP PRE-EXISTING QR CODES=====
            
            
def cleanup_qr_code(qr_path):
    try:
        if os.path.exists(qr_path):
            os.remove(qr_path)
    except Exception as e:
        print(f"Error cleaning up QR code: {str(e)}")


@app.route('/qr/<order_id>')
def generate_qr(order_id):
    order = Order.query.get_or_404(order_id)
    qr = qrcode.make(order.upi_link)
    qr_path = f'static/qr_{order_id}.png'
    qr.save(qr_path)
    return send_file(qr_path, mimetype='image/png', as_attachment=False)
    
    
    
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
    order = Order.query.get(order_id)

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




#=================================================MY ORDERS================================================



@app.route("/my_orders")
def my_orders():
    if "user_email" not in session:
        flash("Please log in to view your orders.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    orders = Order.query.filter_by(user_email=user_email).all()

    return render_template("my_orders.html", orders=orders)



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
        twilio_client.messages.create(body=sms_message, from_=TWILIO_PHONE_NUMBER, to=f"+91{seller.phone}")

        return True
    except Exception as e:
        print(f"Notification error: {str(e)}")
        return False    

    
    

#=================================================PROFILE================================================

    
    

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please login to access your profile.', 'danger')
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        try:
            user.name = request.form.get('name')
            user.phone = request.form.get('phone')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if current_password and new_password and confirm_password:
                if not user.check_password(current_password):
                    flash('Current password is incorrect.', 'danger')
                    return redirect(url_for('profile'))
                
                if new_password != confirm_password:
                    flash('New passwords do not match.', 'danger')
                    return redirect(url_for('profile'))
                
                user.set_password(new_password)

            if user.role == 'vendor':
                user.upi_id = request.form.get('upi_id')
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
            msg = Message(
                'Profile Update Notification',
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]
            )
            msg.body = f"""
Hello {user.name},

Your profile was recently updated. If you did not make these changes, please contact support immediately.

Time of update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Your HomeKitchen Team
            """
            mail.send(msg)
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
            print(f"Profile update error: {str(e)}")
    
    return render_template('profile.html', user=user)




#=================================================DATABASE TO EXCEL================================================

    

import pandas as pd
from sqlalchemy import inspect

def export_all_tables_to_excel(excel_filename='database_export.xlsx'):
    """Exports all tables from the database to an Excel file."""
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            for table_name in inspector.get_table_names():
                df = pd.read_sql_table(table_name, con=engine)
                df.to_excel(writer, sheet_name=table_name, index=False)
        
        print(f"All tables exported to {excel_filename}")

export_all_tables_to_excel()



#=================================================RUN================================================

    
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)