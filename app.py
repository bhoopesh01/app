from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# --- App Initialization and Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Extensions ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Where to send users who are not logged in
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(80), nullable=True)
    income = db.Column(db.String(50), nullable=True)
    monthly_expenses = db.Column(db.String(50), nullable=True) # Changed to String to match form input
    savings_goal = db.Column(db.String(50), nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    financial_goal = db.Column(db.String(80), nullable=True)
    expenses = db.relationship('Expense', backref='owner', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Routes ---

# CHANGE 1: Root URL now directs to login
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            # Redirect to index (main app page) after successful login
            return redirect(url_for('index'))
        else:
            flash('Login Failed. Please check username and password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == request.form.get('username')) | (User.email == request.form.get('email'))).first()
        if existing_user:
            flash('Username or email already exists. Please choose another.', 'danger')
            return redirect(url_for('signup'))
            
        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        new_user = User(
            username=request.form.get('username'), 
            email=request.form.get('email'), 
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        
        # CHANGE 2: Log the user in and redirect to userdetails
        login_user(new_user)
        flash('Your account has been created! Please fill in your details.', 'success')
        return redirect(url_for('userdetails'))
        
    return render_template('signup.html')

@app.route('/userdetails', methods=['GET', 'POST'])
@login_required # This is correct, as the user is now logged in
def userdetails():
    if request.method == 'POST':
        user_to_update = current_user
        user_to_update.full_name = request.form.get('fullName')
        user_to_update.dob = request.form.get('dob')
        user_to_update.phone = request.form.get('phone')
        user_to_update.occupation = request.form.get('occupation')
        user_to_update.income = request.form.get('income')
        user_to_update.monthly_expenses = request.form.get('expenses')
        user_to_update.savings_goal = request.form.get('savingsGoal')
        user_to_update.currency = request.form.get('currency')
        user_to_update.financial_goal = request.form.get('financialGoal')
        db.session.commit()
        
        # CHANGE 3: Flash a confirmation and redirect to the main app page (index/dashboard)
        flash('Your details have been saved successfully!', 'success')
        return redirect(url_for('index')) 
        
    return render_template('userdetails.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Protected Application Pages ---

@app.route('/index')
@login_required
def index():
    user_expenses = Expense.query.filter_by(owner=current_user).all()
    return render_template('index.html', expenses=user_expenses)

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    expense_name = request.form.get('expense-name')
    expense_amount = request.form.get('expense-amount')
    if expense_name and expense_amount:
        new_expense = Expense(name=expense_name, amount=float(expense_amount), owner=current_user)
        db.session.add(new_expense)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.owner == current_user:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

if __name__ == '__main__':
    # It's good practice to create the database contextually
    with app.app_context():
        db.create_all()
    app.run(debug=True)