from flask import Blueprint
from flask_login import login_required, logout_user
from werkzeug.security import check_password_hash
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_user, current_user
from website.models import User
from website import db

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.mot_de_passe, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.list_events'))
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
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')

        mot_de_passe1 = request.form.get('password1')
        mot_de_passe2 = request.form.get('password2')

        date_de_naissance = request.form.get('date_de_naissance')
        civilite = request.form.get('civilite')
        genre = request.form.get('genre')

        # Validation des champs
        if len(email) < 8:
            flash('L\'email doit contenir au moins 8 caractères.', category='error')
        elif len(prenom) < 1:
            flash('Le prénom doit contenir au moins 1 caractère.', category='error')
        elif mot_de_passe1 != mot_de_passe2:
            flash('Les mots de passe ne correspondent pas.', category='error')
        elif len(mot_de_passe1) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', category='error')
        else:
            # Vérifier si l'email existe déjà
            utilisateur_existant = User.query.filter_by(email=email).first()
            if utilisateur_existant:
                flash('L\'email existe déjà.', category='error')
            else:
                # Hasher le mot de passe
                mot_de_passe_hashe = generate_password_hash(mot_de_passe1, method='pbkdf2:sha256')

                # Créer un nouvel utilisateur
                nouvel_utilisateur = User(email=email,
                                          mot_de_passe=mot_de_passe_hashe,
                                          prenom=prenom,
                                          nom=nom,
                                          date_de_naissance=date_de_naissance,
                                          civilite=civilite,
                                          genre=genre)

                # Ajouter et enregistrer le nouvel utilisateur
                db.session.add(nouvel_utilisateur)
                db.session.commit()

                # Connecter l'utilisateur après l'inscription
                login_user(nouvel_utilisateur, remember=True)

                flash('Compte créé avec succès !', category='success')
                return redirect(url_for('views.list_events'))

    return render_template("sign_up.html", user=current_user)
