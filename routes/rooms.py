from services.forms import RoomForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import Salle, db
from flask_login import (
    current_user,
    login_required,
)
r = Blueprint('r', __name__, template_folder="templates")


@r.route('/admin/rooms', methods=["GET", "POST"])
@r.route('/admin/rooms/<isUpdated>', methods=["GET", "POST"])
@login_required
def rooms(isUpdated=True):
    if (current_user.roles[0].id == 1):
        rooms = Salle.query.all()
        add = RoomForm()
        if (add.validate_on_submit()):
            errors = []
            success = False

            for room in rooms:
                if room.name == add.name.data.casefold():
                    errors.append("Room already exists in database")
                elif add.capacity.data < 0:
                    errors.append("Enter a valid capacity")
                    break

            if (not errors):
                room = Salle(name=add.name.data.casefold(
                ), label=add.name.data.capitalize(), capacity=add.capacity.data)
                db.session.add(room)
                db.session.commit()
                success = True
                rooms.append(room)
            add.capacity.data = ""
            add.name.data = ""
            return render_template("/admin/rooms.html", current_user=current_user, rooms=rooms, form=add, errors=errors,
                                   success=success, isUpdated=isUpdated)

        return render_template("/admin/rooms.html", current_user=current_user, rooms=rooms, form=add, isUpdated=isUpdated)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@r.route('/admin/rooms/delete/<roomId>', methods=['POST'])
@login_required
def delete_room(roomId):
    if (current_user.roles[0].id == 1):
        room = Salle.query.filter_by(id=roomId).first()
        if room:
            db.session.delete(room)
            db.session.commit()
        return redirect(url_for("r.rooms"))
    else:
        return render_template("error.html", name='ADMIN', error=401)


@r.route('/admin/rooms/update/<roomId>', methods=['POST'])
@login_required
def update_module(roomId):
    """update a room."""
    if (current_user.roles[0].id == 1):
        update = RoomForm()
        room = Salle.query.filter_by(id=roomId).first()
        if room and update.name.data and update.capacity.data:
            isUpdated = True
            isExist = Salle.query.filter_by(
                name=update.name.data.casefold()).one_or_none()
            if not isExist:
                room.name = update.name.data.casefold()
                room.label = update.name.data.capitalize()
                room.capacity = update.capacity.data
            elif isExist.name == room.name:
                room.capacity = update.capacity.data
            else:
                isUpdated = False
            db.session.commit()
            return redirect(url_for("r.rooms", isUpdated=isUpdated))
    else:
        return render_template("error.html", name='ADMIN', error=401)
