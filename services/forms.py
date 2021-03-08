from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Email

#################Forms###################


class ExamForm(FlaskForm):
    date = DateField('Plan Start', validators=[
                     DataRequired()], format='%Y-%m-%d')
    start_at = TimeField('Start at', validators=[DataRequired()])
    end_at = TimeField('End at', validators=[DataRequired()])
    branch = SelectField('Filiere', coerce=str)
    semester = SelectField('Semestre', coerce=str)
    module = SelectField('Module', coerce=int)
    salle = SelectField('Salle', coerce=int)
    responsable = SelectField('Responsable', coerce=int)


class BranchForm(FlaskForm):
    name = StringField('Branch Name', validators=[DataRequired()])


class SemesterForm(FlaskForm):
    name = StringField('Semester Name', validators=[DataRequired()])


class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email address', validators=[DataRequired()])
    role = SelectField('Role', coerce=str)
    apogee = StringField('Apogee')
    uuid = StringField('UUID')
    classe = SelectField('Class', coerce=str)


class RoomForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    capacity = IntegerField('capacity', validators=[DataRequired()])


class ModuleForm(FlaskForm):
    name = StringField('module name', validators=[DataRequired()])


class ClassForm(FlaskForm):
    branch = SelectField('Filiere', coerce=str)
    semester = SelectField('Semestre', coerce=str)
