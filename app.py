#imports
from flask import Flask, request, redirect, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_security.forms import RegisterForm, ConfirmRegisterForm
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_mail import Mail
from werkzeug.contrib.fixers import ProxyFix

# app configs
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test123@localhost/flaskbook'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSOPO'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'backsideburner@gmail.com'
app.config['MAIL_PASSWORD'] = 'iamthekingofmyworld'
mail = Mail()
mail.init_app(app)
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)
db = SQLAlchemy(app)


# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


# Define tables
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])

class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
         register_form=ExtendedRegisterForm,
         confirm_register_form=ExtendedConfirmRegisterForm)

# Drop and Create
# @app.before_first_request
# def create_user():
#     db.drop_all()
#     db.create_all()
#     # user_datastore.create_user(email='matt@nobien.net', password=encrypt_password('password'))
#     db.session.commit()

# Views
@app.route('/nav')
def navigate():
    return render_template('navigate.html')

@app.route('/')
@login_required
def home():
    user_id = session["user_id"]
    current = User.query.filter_by(id=user_id).first()
    user_name = current.first_name
    return render_template('home.html', user_name=user_name)

@app.route('/aboutus')
def about():
    return render_template('about_us.html')

if __name__ == '__main__':
    app.run()