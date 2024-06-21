from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.models import User, gdd_personne  # Adjust import path based on your project structure
from website import db  # Assuming db is the SQLAlchemy instance

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 8:
            flash('Email must be greater than 8 characters.', category='error')
        elif len(first_name) < 1:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            new_user = User(email=email,password=hashed_password)
            db.session.add(new_user)

            user = User.query.filter_by(email=email).first()
            gdd_user = gdd_personne(id_personne= user.id,login=email, nom=first_name)

            db.session.add(gdd_user)

            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
