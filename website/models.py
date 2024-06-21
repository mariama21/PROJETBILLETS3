from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from website import db


class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    # Login
    email = db.Column(String(150), unique=True, nullable=False)
    mot_de_passe = db.Column(String(150), nullable=False)
    type_utilisateur = db.Column(String(50), nullable=False, default='utilisateur')
    est_actif = db.Column(Boolean, default=True)

    # Infos
    prenom = db.Column(String(150), nullable=False)
    nom = db.Column(String(150), nullable=False)
    date_de_naissance = db.Column(db.Date)
    civilite = db.Column(String(10))  # Exemple: 'M.', 'Mme', 'Mlle', etc.
    genre = db.Column(String(10))  # Exemple: 'Homme', 'Femme', 'Autre'

    # Time
    cree_le = db.Column(DateTime, default=datetime.now)
    mis_a_jour_le = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    events = relationship('Event', backref='user', lazy=True)
    reservations = relationship('Reservation', backref='client', lazy=True)

    def __repr__(self):
        return f"Utilisateur('{self.email}', '{self.prenom}', '{self.nom}')"


class Event(db.Model):
    __tablename__ = 'gdd_event'

    id_event = Column(Integer, primary_key=True, autoincrement=True)
    nom_event = Column(String(100), nullable=False)
    statut = Column(String(45))
    alias_event = Column(String(100))
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    categorie = Column(String(45))
    description = Column(Text(collation='utf8mb4_unicode_ci'))
    adresse_rue = Column(String(200))
    adresse_cp = Column(String(45))
    adresse_ville = Column(String(45))
    adresse_pays = Column(String(45))
    uuid_event = Column(String(200))
    Actif = Column(Boolean, default=True)
    Type = Column(String(45))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # Relationships
    reservations = relationship('Reservation', backref='event', lazy=True)

    def __repr__(self):
        return f"Event(id_event={self.id_event}, nom_event='{self.nom_event}')"


class Reservation(db.Model):
    id_reservation = db.Column(Integer, primary_key=True)
    id_client = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    id_event = db.Column(Integer, ForeignKey('gdd_event.id_event'), nullable=False)
    statut = db.Column(String(50), nullable=False, default='attente')

    def __repr__(self):
        return f"Reservation(id_reservation={self.id_reservation}, id_client={self.id_client}, id_event={self.id_event})"
