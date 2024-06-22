from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from website.models import Event, Reservation
from website import db

views = Blueprint('views', __name__)


def get_filtered_events(events, search_query=None, filter_type=None, filter_category=None):
    if filter_type:
        events = [event for event in events if event.Actif] if filter_type == 'Actif' else [event for event in events if
                                                                                            not event.Actif]

    if search_query:
        events = [event for event in events if search_query.lower() in event.nom_event.lower()]

    if filter_category and filter_category != 'Tous':
        events = [event for event in events if event.categorie == filter_category]

    return events


@views.route('/', methods=['GET', 'POST'])
def list_events():
    all_events = Event.query.all()
    categories = {event.categorie for event in all_events}

    search_query = request.form.get('searchQuery')
    filter_type = request.form.get('filterType')
    filter_category = request.form.get('filterCategory')

    if filter_type == 'Actif':
        all_events = [event for event in all_events if event.Actif]
    elif filter_type == 'Passif':
        all_events = [event for event in all_events if not event.Actif]

    if search_query:
        all_events = [event for event in all_events if search_query.lower() in event.nom_event.lower()]

    if filter_category and filter_category != 'Tous':
        all_events = [event for event in all_events if event.categorie == filter_category]

    user_reservations = set()
    if current_user.is_authenticated:
        user_reservations = {reservation.id_event for reservation in current_user.reservations}

    return render_template("event/list_event.html",
                           events=all_events,
                           categories=categories,
                           current_filter_type=filter_type,
                           current_filter_category=filter_category,
                           user=current_user,
                           user_reservations=user_reservations)


@views.route("/add-event", methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        try:
            new_event = Event(
                nom_event=request.form.get('nom_event'),
                statut=request.form.get('statut'),
                alias_event=request.form.get('alias_event'),
                date_debut=datetime.strptime(request.form.get('date_debut'), '%Y-%m-%dT%H:%M') if request.form.get(
                    'date_debut') else None,
                date_fin=datetime.strptime(request.form.get('date_fin'), '%Y-%m-%dT%H:%M') if request.form.get(
                    'date_fin') else None,
                categorie=request.form.get('categorie'),
                description=request.form.get('description'),
                adresse_rue=request.form.get('adresse_rue'),
                adresse_cp=request.form.get('adresse_cp'),
                adresse_ville=request.form.get('adresse_ville'),
                adresse_pays=request.form.get('adresse_pays'),
                nombre_places=request.form.get('nombre_places'),
                uuid_event=request.form.get('uuid_event'),
                user_id=current_user.id,
                Actif=True if request.form.get('Actif') == '1' else False,
                Type=request.form.get('Type')
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Événement ajouté avec succès!', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout de l\'événement: {str(e)}', category='error')
        return redirect(url_for('views.add_event'))

    return render_template("event/add_event.html", user=current_user)


@views.route('event/delete/<id>/', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    try:
        event = Event.query.get(id)
        db.session.delete(event)
        db.session.commit()
        flash('Événement supprimé avec succès!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de l\'événement: {str(e)}', category='error')
    return redirect(url_for('views.list_mes_events'))


@views.route('/event/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)

    if request.method == 'POST':
        try:
            event.nom_event = request.form.get('nom_event')
            event.statut = request.form.get('statut')
            event.alias_event = request.form.get('alias_event')
            event.date_debut = datetime.strptime(request.form.get('date_debut'), '%Y-%m-%dT%H:%M') if request.form.get(
                'date_debut') else None
            event.date_fin = datetime.strptime(request.form.get('date_fin'), '%Y-%m-%dT%H:%M') if request.form.get(
                'date_fin') else None
            event.categorie = request.form.get('categorie')
            event.description = request.form.get('description')
            event.adresse_rue = request.form.get('adresse_rue')
            event.adresse_cp = request.form.get('adresse_cp')
            event.adresse_ville = request.form.get('adresse_ville')
            event.adresse_pays = request.form.get('adresse_pays')
            event.uuid_event = request.form.get('uuid_event')
            event.Actif = True if request.form.get('Actif') == '1' else False
            event.Type = request.form.get('Type')
            db.session.commit()
            flash('Événement modifié avec succès!', category='success')
            return redirect(url_for('views.list_events'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification de l\'événement: {str(e)}', category='error')

    return render_template("event/edit_event.html", event=event, user=current_user)


@views.route('/list-mes-events', methods=['GET', 'POST'])
@login_required
def list_mes_events():
    all_events = Event.query.filter_by(user_id=current_user.id).all()
    categories = {event.categorie for event in all_events}

    search_query = request.form.get('searchQuery')
    filter_type = request.form.get('filterType')
    filter_category = request.form.get('filterCategory')

    filtered_events = get_filtered_events(all_events, search_query, filter_type, filter_category)

    return render_template("event/my_event.html",
                           events=filtered_events,
                           categories=categories,
                           current_filter_type=filter_type,
                           current_filter_category=filter_category,
                           user=current_user)


@views.route('/event/reserve/<int:event_id>/', methods=['POST'])
@login_required
def reserve_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.nombre_places > 0:
        # Créer une nouvelle réservation
        new_reservation = Reservation(
            id_client=current_user.id,
            id_event=event_id,
            statut='attente'
        )

        # Décrémenter le nombre de places disponibles
        event.nombre_places -= 1

        # Ajouter la réservation à la base de données
        db.session.add(new_reservation)
        db.session.commit()

        flash('Réservation effectuée avec succès!', category='success')
    else:
        flash('Désolé, plus de places disponibles pour cet événement.', category='error')

    return redirect(url_for('views.list_events'))


@views.route('event/cancel/<int:event_id>/', methods=['POST'])
@login_required
def cancel_reservation(event_id):
    reservation = Reservation.query.filter_by(id_event=event_id, id_client=current_user.id).first()

    event = reservation.event

    if reservation:
        db.session.delete(reservation)
        event.nombre_places += 1
        db.session.commit()
        flash('Réservation annulée avec succès!', category='success')
    else:
        flash('Réservation non trouvée!', category='error')
    return redirect(url_for('views.list_events'))


@views.route('/list_reservation', methods=['GET'])
@login_required
def list_reservations():
    reservations = Reservation.query.filter_by(id_client=current_user.id).all()
    events = [reservation.event for reservation in reservations]
    return render_template("reservation/my_reservation.html", events=events,
                           user=current_user)


@views.route('/event/reservations/<int:event_id>/', methods=['GET'])
@login_required
def event_reservations(event_id):
    # Vérifier si l'utilisateur est le créateur de l'événement
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)  # Interdire l'accès si l'utilisateur n'est pas le créateur de l'événement

    # Récupérer les réservations pour cet événement
    reservations = Reservation.query.filter_by(id_event=event_id).all()

    return render_template("reservation/event_reservation.html",
                           event=event,
                           reservations=reservations,
                           user=current_user)


@views.route('/event/confirm-reservation/<int:reservation_id>/', methods=['POST'])
@login_required
def confirm_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    # Vérifier si l'utilisateur est le créateur de l'événement associé à cette réservation
    event = Event.query.get_or_404(reservation.id_event)
    if event.user_id != current_user.id:
        abort(403)  # Interdire l'accès si l'utilisateur n'est pas le créateur de l'événement

    # Vérifier si des places sont disponibles
    if event.nombre_places <= 0:
        flash('Désolé, il n\'y a plus de places disponibles pour cet événement.', category='error')
        return redirect(url_for('views.event_reservations', event_id=event.id_event))

    # Mettre à jour le statut de la réservation à "confirmé"
    reservation.statut = 'confirmé'
    event.nombre_places -= 1  # Réduire le nombre de places disponibles
    db.session.commit()

    flash('Réservation confirmée avec succès!', category='success')
    return redirect(url_for('views.event_reservations', event_id=reservation.id_event))
