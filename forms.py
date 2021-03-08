from flask_wtf import FlaskForm
from wtforms import StringField, SelectField , IntegerField, SelectMultipleField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Email

#################Forms###################


class ExamForm(FlaskForm):
    date = DateField('Plan Start', validators=[DataRequired()], format='%Y-%m-%d')
    start_at = TimeField('Start at', validators=[DataRequired()])
    end_at = TimeField('End at', validators=[DataRequired()])
    module = SelectField('Module', coerce=int)
    responsable = SelectField('Responsable', coerce=int)


class BranchForm(FlaskForm):
    branch_name = StringField('Branch Name', validators=[DataRequired()])


class SemesterForm(FlaskForm):
    semester_name = StringField('Semester Name', validators=[DataRequired()])

class StudentForm(FlaskForm):
    name = StringField('Name')
    email = StringField('Email address')
    apogee = StringField('Apogee')
    uuid = StringField('UUID')
    # name = StringField('Name', validators=[DataRequired()])
    # email = StringField('Email address', validators=[DataRequired()])
    # apogee = StringField('Apogee', validators=[DataRequired()])
    # uuid = StringField('UUID', validators=[DataRequired()])
    classe = SelectField('Class', coerce=str)
    role = SelectField('Role',coerce=str)
    
class RoomForm(FlaskForm):
    name = StringField('name',validators=[DataRequired()])
    capacity = IntegerField('capacity',validators=[DataRequired()])

class ModuleForm(FlaskForm):
    name = StringField('module name', validators=[DataRequired()])

class ClassForm(FlaskForm):
    branch = SelectField('Filiere', coerce=str)
    semester = SelectField('Semestre', coerce=str)

