from services.forms import SemesterForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import Semester, db
from flask_login import (
    current_user,
    login_required,
)
s = Blueprint('s', __name__, template_folder='templates')


@s.route('/admin/semesters', methods=["GET", "POST"])
@s.route('/admin/semesters/<isUpdated>', methods=["GET", "POST"])
@login_required
def semesters(isUpdated=True):
    add = SemesterForm()
    semesters = db.session.query(Semester).all()
    if current_user.roles[0].id == 1:
        if add.validate_on_submit():
            errors = []
            success = False
            if not add.name.data:
                errors.append("Name Field Required")
            else:
                for semester in semesters:
                    if semester.name == add.name.data.casefold():
                        errors.append("Semester already exists")
            if not errors:
                semester = Semester(name=add.name.data.casefold(),label = add.name.data.capitalize())
                db.session.add(semester)
                db.session.commit()
                semesters.append(semester)
                success = True
            return render_template("/admin/semesters.html", success=success, current_user=current_user, form=add,
                                   errors=errors, semesters=semesters, isUpdated=isUpdated)
        return render_template("/admin/semesters.html", current_user=current_user, form=add, semesters=semesters, isUpdated=isUpdated)

    else:
        return render_template("error.html", name='ADMIN', error=401)


@s.route('/admin/semesters/delete/<semesterId>', methods=['POST'])
@login_required
def delete_semester(semesterId):
    if (current_user.roles[0].id == 1):
        semes = Semester.query.get_or_404(semesterId)
        if semes:
            db.session.delete(semes)
            db.session.commit()
        return redirect(url_for('s.semesters'))
    else:
        return render_template("error.html", name='ADMIN', error=401)


@s.route('/admin/semesters/update/<semesterId>', methods=['POST', 'GET'])
@login_required
def update_semester(semesterId):
    """update a semester"""
    if(current_user.roles[0].id == 1):
        update = SemesterForm()
        semester = Semester.query.filter_by(id=semesterId).first()
        if semester and update.name.data:
            isUpdated = True
            isExist = Semester.query.filter_by(
                name=update.name.data.casefold()).one_or_none()
            if not isExist:
                semester.name = update.name.data.casefold()
                semester.label = update.name.data.capitalize()
            else:
                isUpdated = False
            db.session.commit()
            return redirect(url_for('s.semesters', isUpdated=isUpdated))
    else:
        return render_template("error.html", name='ADMIN', error=401)
