from services.forms import ClassForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import Class, Branch, Semester, db
from flask_login import (
    current_user,
    login_required,
)
c = Blueprint('c', __name__, template_folder='templates')


@c.route('/admin/classes', methods=["GET", "POST"])
@c.route('/admin/classes/<isUpdated>', methods=["GET", "POST"])
@login_required
def classes(isUpdated=True):
    if(current_user.roles[0].id == 1):
        classes = Class.query.all()
        add = ClassForm()
        branches = Branch.query.all()
        semesters = Semester.query.all()
        branches_list = [b.label for b in branches]
        semesters_list = [s.label for s in semesters]
        add.branch.choices = branches_list
        add.semester.choices = semesters_list
        if(add.validate_on_submit()):
            errors = []
            success = False
            classe = Class.query.filter_by(name=(
                add.branch.data+'-'+add.semester.data)).one_or_none()
            if classe:
                errors.append("Class with branch {} and semester {} already exists".format(
                    add.branch.data, add.semester.data))
            if not errors:
                classe = Class(name=add.branch.data+'-' +
                               add.semester.data, capacity=0)
                db.session.add(classe
                               )
                db.session.commit()
                success = True
                classes.append(classe)
            return render_template("/admin/classes.html", current_user=current_user, classes=classes, form=add, errors=errors, success=success, isUpdated=isUpdated)
        return render_template("/admin/classes.html", current_user=current_user, classes=classes, form=add, isUpdated=isUpdated)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@c.route('/admin/classes/delete/<classeId>', methods=['POST'])
@login_required
def delete_classe(classeId):
    """Delete a class."""
    if(current_user.roles[0].id == 1):
        classe = Class.query.filter_by(id=classeId).first()
        if classe:
            db.session.delete(classe)
            db.session.commit()
        return redirect(url_for("c.classes"))
    else:
        return 'Unauthorized action'


@c.route('/admin/classes/update/<classId>', methods=['POST', 'GET'])
@login_required
def update_classe(classId):
    """Update a class."""
    if(current_user.roles[0].id == 1):
        update = ClassForm()
        classe = Class.query.filter_by(id=classId).first()
        if(classe and update.branch.data and update.branch.data):
            isUpdated = True
            isExist = Class.query.filter_by(
                name=update.branch.data+'-'+update.semester.data).one_or_none()
            if not isExist or classe.name == update.branch.data+'-'+update.semester.data:
                classe.name = update.branch.data+'-'+update.semester.data
            else:
                isUpdated = False
            db.session.commit()
            return redirect(url_for('c.classes', isUpdated=isUpdated))
    else:
        return render_template("error.html", name='ADMIN', error=401)
