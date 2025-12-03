from flask import (Blueprint, request, jsonify, 
                    render_template, url_for, redirect,session)
from models.users import Users
from utils.database import SessionLocal


user = Blueprint("user", __name__)

db = SessionLocal()

# Create user route
@user.route('/register', methods=['GET', 'POST'])
def user_create():
    message = None
    message_type = None    # success or danger for Bootstrap

    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get("password")


        # Check existing email
        if db.query(Users).filter_by(email=email).first():
            message = "Email already registered!"
            message_type = "danger"
            return render_template("create_user.html", message=message, message_type=message_type)

        # Create new user
        new_user = Users(username=username, email=email)
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        db.close()

        message = "User registered successfully!"
        message_type = "success"
        return render_template("create_user.html", message=message, message_type=message_type)

    return render_template("create_user.html", message=message, message_type=message_type)



@user.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.query(Users).filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))

        return "Invalid credentials", 401

    return render_template('login.html')

@user.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))





