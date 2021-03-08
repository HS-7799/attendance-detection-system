from services.forms import UserForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import *
from flask_login import (
    current_user,
    login_required,
)
import re
# regex = '^[A-Za-z0-9._%+-]+@uit.ac.ma$'
regex = '^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$'
u = Blueprint('u', __name__, template_folder='templates')


@u.route('/admin/users', methods=['GET', 'POST'])
def users():
    errors = None
    success = None
    if "errors" in request.args:
        errors = request.args['errors']
    if "success" in request.args:
        success = request.args['success']
    if current_user.roles[0].id == 1:
        add = UserForm()
        classes = db.session.query(Class).all()
        roles = db.session.query(Role).all()
        roles_list = [(b.id, b.name) for b in roles]
        classes_list = [(s.id, s.name) for s in classes]
        add.role.choices = roles_list
        add.classe.choices = classes_list
        users = User.query.all()
        return render_template("/admin/users.html", current_user=current_user, users=users, form=add, errors=errors, success=success)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@u.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.roles[0].id == 1:
        add = UserForm()
        classes = db.session.query(Class).all()
        roles = db.session.query(Role).all()
        roles_list = [(b.id, b.name) for b in roles]
        classes_list = [(s.id, s.name) for s in classes]
        add.role.choices = roles_list
        add.classe.choices = classes_list

        if (add.validate_on_submit()):
            errors = []
            success = False
            if not add.name.data:
                errors.append("Name field is required")
            if not add.email.data:
                errors.append("Email field is required")
            elif not re.search(regex, add.email.data):
                errors.append("Invalid Email")
            if add.role.data == "4":
                if not add.apogee.data:
                    errors.append("Apogee field is required")
                elif not re.search("[0-9]{8}", add.apogee.data):
                    errors.append("Apogee length must include 8 digits")
                if not add.uuid.data:
                    errors.append("UUID field is required")


            users = db.session.query(User).all()

            for user in users:
                if user.email == add.email.data:
                    errors.append("Email is taken by another user")
                    break
                if user.apogee == add.apogee.data:
                    errors.append("Apogee is taken by another Student")
                    break
                if user.uuid == add.uuid.data:
                    errors.append("UUID is already taken by another Student")

            if not errors:
                if add.role.data == "4":
                    newStudent = User(name=add.name.data, email=add.email.data, apogee=add.apogee.data,
                                      uuid=add.uuid.data, class_id=add.classe.data)
                    classe = Class.query.filter_by(id=add.classe.data).first()
                    newStudent.classe = classe
                    newStudent.classe.capacity = newStudent.classe.capacity+1
                else:
                    newStudent = User(name=add.name.data,
                                      email=add.email.data)
                    # add student role
                role = Role.query.filter_by(id=add.role.data).first()
                newStudent.roles.append(role)
                db.session.add(newStudent)
                db.session.commit()
                success = True
            return render_template("/admin/add_user.html", success=success, current_user=current_user, form=add,
                                       errors=errors)
        return render_template("/admin/add_user.html", current_user=current_user, form=add)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@u.route('/admin/users/delete/<userId>', methods=['POST', 'GET'])
def delete(userId):
    if (current_user.roles[0].id == 1):
        user = User.query.filter_by(id=userId).first()
        if user:
            for user_examen in user.user_examen:
                db.session.delete(user_examen)
            user.classe.capacity = user.classe.capacity-1
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for("u.users"))
    else:
        return render_template("error.html", name='ADMIN', error=401)


@u.route('/admin/users/update/<userId>', methods=['POST', 'GET'])
def update(userId):
    if (current_user.roles[0].id == 1):
        update = UserForm()
        user = User.query.filter_by(id=userId).first()
        if user and update.name.data and update.email.data:
            errors = []
            success = False
            isExist = User.query.filter_by(
                email=update.email.data).one_or_none()
            if not update.name.data:
                errors.append("Name field is required")
            if not update.email.data:
                errors.append("Email field is required")
            elif not re.search(regex, update.email.data):
                errors.append("Invalid Email")
            if update.role.data == 4:
                if not update.apogee.data:
                    errors.append("Apogee field is required")
                elif not re.search("[0-9]{8}", update.apogee.data):
                    errors.append("Apogee length must include 8 digits")
                if not update.uuid.data:
                    errors.append("UUID field is required")
            users = db.session.query(User).all()
            if user.email != update.email.data:
                for user1 in users:
                    if user1.email == update.email.data:
                        errors.append("Email is taken by another user")
                        break
            if user.apogee != update.apogee.data:
                for user1 in users:
                    if user1.apogee == update.apogee.data:
                        errors.append("Apogee is taken by another Student")
                        break
            if user.uuid != update.uuid.data:
                for user1 in users:
                    if user.uuid == update.uuid.data:
                        errors.append(
                            "UUID is already taken by another Student")

            if (not isExist or user.email == update.email.data) and not errors:
                user.email = update.email.data
                user.name = update.name.data
                if int(update.role.data) == 4:
                    user.apogee = update.apogee.data
                    user.uuid = update.uuid.data
                    if user.roles[0].id == 4:
                        classe = Class.query.filter_by(
                            id=update.classe.data).one_or_none()
                        classe.students.append(user)
                        classe.capacity = classe.capacity+1
                        user.classe.capacity = user.classe.capacity+1
                    if user.class_id != update.classe.data and user.roles[0].id == 4:
                        user.classe.capacity = user.classe.capacity-1
                        user.classe = None
                        user.classe_id = update.classe.data
                        user.classe = Class.query.filter_by(
                            id=update.classe.data).first()
                        user.classe.capacity = user.classe.capacity+1
                else:
                    if user.roles[0].id == 4:
                        user.apogee = None
                        user.uuid = None
                        user.classe.capacity = user.classe.capacity-1
                        user.classe = None
                        user.classe_id = None

                if user.roles[0].id != update.role.data:
                    role = Role.query.filter_by(id=user.roles[0].id).first()
                    role1 = Role.query.filter_by(id=update.role.data).first()
                    user.roles.remove(role)
                    user.roles.append(role1)
                success = True
            db.session.commit()
            return redirect(url_for("u.users", errors=errors, success=success))
    else:
        return render_template("error.html", name='ADMIN', error=401)
