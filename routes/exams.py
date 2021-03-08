from services.forms import ExamForm
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import *
from flask_login import (
    current_user,
    login_required,
)
from datetime import date,datetime
e = Blueprint('e', __name__, template_folder="templates")


@e.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    if (current_user.roles[0].id == 1):
        examens = Examen.query.all()
        return render_template("/admin/exams.html", current_user=current_user, examens=examens)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@e.route('/admin/add', methods=["GET"])
@login_required
def add_exam_create():

    add = ExamForm()
    salles = db.session.query(Salle).all()
    modules = db.session.query(Module).all()

    responsables = db.session.query(User).filter(User.roles.any(id=3)).all()
    responsables_list = [(r.id, r.name) for r in responsables]
    modules_list = [(m.id, m.label) for m in modules]

    add.responsable.choices = responsables_list
    add.module.choices = modules_list

    return render_template("/admin/add_exam.html", current_user=current_user, form=add, rooms=salles)


@e.route('/admin/add', methods=["POST"])
@login_required
def add_exam():
    if (current_user.roles[0].id == 1):
        errors = []
        success = False
        add = ExamForm()
        rooms = db.session.query(Salle).all()
        modules = db.session.query(Module).all()
        modules_list = [(m.id, m.label) for m in modules]
        add.module.choices = modules_list

        responsables = db.session.query(
            User).filter(User.roles.any(id=3)).all()
        responsables_list = [(r.id, r.name) for r in responsables]
        add.responsable.choices = responsables_list
        exam_rooms = request.form.getlist('examRooms')
        if (add.start_at.data > add.end_at.data):
            errors.append("Start time must be less than end time")
        if (add.date.data < date.today()):
            errors.append("Date of the exam must be either today or in the future")
        elif (add.date.data == date.today()):
            Time = datetime.now()
            Current_Time = Time.strftime("%H:%M:%S")
            if str(add.start_at.data) < Current_Time:
                errors.append("Exam today but start time is already passed")
        module = Module.query.filter_by(id=add.module.data).first()
        if not module:
            errors.append("This exam concern which module ?")

        e = Examen(date=add.date.data, start=add.start_at.data,
                   end=add.end_at.data, status=0, module_id=add.module.data)
        if len(exam_rooms) == 0:
            errors.append("In which room(s) this exam will take place ?")
        else:
            for salle_id in exam_rooms:
                salle = Salle.query.filter_by(id=salle_id).first()
                e.salles.append(salle)
                for examen in salle.examens:
                    if (examen.id == e.id):
                        continue
                    if examen.date == e.date:
                        if (((e.start >= examen.start and e.start <= examen.end) or (
                            e.start <= examen.start and e.end <= examen.end and e.end >= examen.start)) and e.salles[
                                0].id == examen.salles[0].id):
                            errors.append("Room ' {} ' Occupied between {} and {} by another exam in {}".format(
                                examen.salles[0].name, examen.start, examen.end, examen.date))
        if not errors:
            db.session.commit()
            success = True
            classes = Class.query.all()
            classes_forsalle = []
            for salle in e.salles:
                examen_salle = Examen_Salle.query.filter_by(
                    examen_id=e.id, salle_id=salle.id).first()
                classes_forsalle.append(examen_salle.classes)
            return render_template("/admin/one_exam.html", exam=e, module=e.module, rooms=zip(e.salles, classes_forsalle), classes=classes)

        return render_template("/admin/add_exam.html", current_user=current_user, form=add, rooms=rooms, errors=errors, success=success)

    else:
        return render_template("error.html", name='ADMIN', error=401)



@e.route('/admin/exams/delete/<examId>', methods=['GET', 'POST'])
@login_required
def delete_exam(examId):
    """Delete exam"""
    if(current_user.roles[0].id == 1):
        exam = Examen.query.filter_by(id=examId).first()
        examen_salle = Examen_Salle.query.filter_by(examen_id=examId).all()
        if exam:
            for i in examen_salle:
                print(i.classes)
                i.classes.clear()
                print(i.classes)
                # db.session.delete(i)
            for user_examen in exam.user_examen:
                db.session.delete(user_examen)
            db.session.delete(exam)
            db.session.commit()
        return redirect(url_for("e.admin"))
    else:
        return render_template("error.html", name='ADMIN', error=401)


@e.route('/admin/exams/details/<examId>', methods=["GET"])
@login_required
def get_exam_details(examId):
    if (current_user.roles[0].id == 1):
        exam = Examen.query.filter_by(id=examId).first()
        if not exam:
            return render_template("error.html", name='ADMIN', error=401)
        else:
            users = []
            for user_examen in exam.user_examen:
                print(user_examen)
        return render_template("/admin/exam_room_students.html",)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@e.route('/admin/exams/<examId>', methods=["GET"])
@login_required
def get_exam(examId):
    if (current_user.roles[0].id == 1):
        exam = Examen.query.filter_by(id=examId).first()
        if not exam:
            return render_template("error.html", name='ADMIN', error=401)
        else:
            classes = Class.query.all()
            classes_forsalle = []
            for salle in exam.salles:
                examen_salle = Examen_Salle.query.filter_by(
                    examen_id=examId, salle_id=salle.id).first()
                classes_forsalle.append(examen_salle.classes)
            for classe in classes:
                classe.classes_forsalle = classes_forsalle
            return render_template("/admin/one_exam.html", exam=exam, module=exam.module, rooms=zip(exam.salles, classes_forsalle), classes=classes)
    else:
        return render_template("error.html", name='ADMIN', error=401)


@e.route('/admin/exams/<examId>/salles/<salleId>', methods=["POST"])
@login_required
def set_exam_classes(examId, salleId):
    if (current_user.roles[0].id == 1):
        examen_salle = Examen_Salle.query.filter_by(examen_id=examId, salle_id=salleId).one_or_none()
        
        if not examen_salle:
            return render_template("error.html", name='ADMIN', error=401)
        else:
            errors = []
            exam_classes = request.form.getlist('examClasses[]')
            for classe_id in exam_classes:
                
                classex = Class.query.filter_by(id=classe_id).first()
                for examen_salle in classex.examen_salle:
                    if str(examen_salle.examen_id) == examId:
                        errors.append("This class is already in another room")
                        
                if not errors:
                    classex.examen_salle.append(examen_salle)
                    e = Examen.query.filter_by(id=examId).first()
                    for student in classex.students:
                        ue = User_Examen(user_id=student.id,
                                        examen_id=e.id, etat=0)
                        student.user_examen.append(ue)
                        e.user_examen.append(ue)
                        db.session.add(ue)
        db.session.commit()
        exam = Examen.query.filter_by(id=examId).first()
        return redirect(url_for('e.get_exam', examId=examId))
    else:
        return render_template("error.html", name='ADMIN', error=401)



@e.route('/admin/exams/details/<examId>&<salleId>', methods=["GET"])
@login_required
def get_exam_details_perclass(examId, salleId):
    if (current_user.roles[0].id == 1):
        users = []
        exam = Examen.query.filter_by(id=examId).first()
        examen_salle = Examen_Salle.query.filter_by(
            examen_id=examId, salle_id=salleId).one_or_none()
        for classe in examen_salle.classes:
            for user_examen in exam.user_examen:
                if user_examen.user.class_id == classe.id:
                    users.append(user_examen)
        if not exam:
            return render_template("error.html", name='Not Found', error=404)
        salle = Salle.query.filter_by(id=salleId).first()
        return render_template("/admin/exam_room_students.html", exam=exam, salle=salle, classes=examen_salle.classes, users=users)
    else:
        return render_template("error.html", name='ADMIN', error=401)
