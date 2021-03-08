from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from typing import Callable


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Table: Callable
    ForeignKey: Callable
    ForeignKeyConstraint: Callable
    PrimaryKeyConstraint: Callable
    relationship: Callable
    backref: Callable
    Boolean: Callable
    Time: Callable
    Date: Callable


db = MySQLAlchemy()

############Database#########
user_role = db.Table('user_role',
                     db.Column('user_id', db.Integer, db.ForeignKey(
                         'user.id'), primary_key=True),
                     db.Column('role_id', db.Integer, db.ForeignKey(
                         'role.id'), primary_key=True)
                     )
examen_classe = db.Table('examen_classe',
                         db.Column('examen_id', db.Integer, db.ForeignKey(
                             'examen.id'), primary_key=True),
                         db.Column('class_id', db.Integer, db.ForeignKey(
                             'class.id'), primary_key=True)
                         )
examen_salle_classe = db.Table('examen_salle_classe',
                               db.Column('examen_id', db.Integer),
                               db.Column('salle_id', db.Integer),
                               db.Column('class_id', db.Integer,
                                         db.ForeignKey("class.id")),
                               db.ForeignKeyConstraint(
                                   ['examen_id', 'salle_id'],
                                   ['examen_salle.examen_id',
                                       'examen_salle.salle_id']
                               ))


class Examen_Salle(db.Model):
    __tablename__ = 'examen_salle'
    examen_id = db.Column(db.Integer, db.ForeignKey(
        'examen.id'), primary_key=True)
    salle_id = db.Column(db.Integer, db.ForeignKey(
        'salle.id'), primary_key=True)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    label = db.Column(db.String(70))
    examens = db.relationship('Examen', backref='module', lazy=True)


class Salle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    label = db.Column(db.String(70))
    capacity = db.Column(db.Integer)


class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    label = db.Column(db.String(70))


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    label = db.Column(db.String(70))


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    capacity = db.Column(db.Integer)
    students = db.relationship('User', backref='classe', lazy=True)
    examen_salle = db.relationship(
        "Examen_Salle", secondary=examen_salle_classe, backref="classes")


class User_Examen(db.Model):
    __tablename__ = 'user_examen'
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), primary_key=True)
    examen_id = db.Column(db.Integer, db.ForeignKey(
        'examen.id'), primary_key=True)
    etat = db.Column(db.Boolean, default=0)
    start = db.Column(db.String)
    end = db.Column(db.String)

    def __repr__(self):
        # return '<User {} In Exam {} Etat {}>'.format(self.user_id, self.examen_id, self.etat)
        return '{}'.format(self.examen_id)


class User(db.Model, UserMixin):
    """ Create user table """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(80), unique=True)
    roles = db.relationship('Role', secondary=user_role, lazy='subquery',
                            backref=db.backref('users', lazy=True))
    ##########Only for students###########
    apogee = db.Column(db.String(80), unique=False)
    uuid = db.Column(db.String(80), unique=True, nullable=True)
    user_examen = db.relationship('User_Examen', backref='user',
                                  primaryjoin=id == User_Examen.user_id)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __repr__(self):
        return '<User %r >' % self.name


class Role(db.Model):
    """ Create role table """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)


class Examen(db.Model):
    """ Create examen table """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    start = db.Column(db.Time)
    end = db.Column(db.Time)
    status = db.Column(db.Integer)
    salles = db.relationship('Salle', secondary='examen_salle', lazy='subquery',
                             backref=db.backref('examens', lazy=True))
    user_examen = db.relationship('User_Examen', backref='examen',
                                  primaryjoin=id == User_Examen.examen_id)
    classes = db.relationship('Class', secondary=examen_classe, lazy='subquery',
                              backref=db.backref('examens', lazy=True))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))

    def __repr__(self):
        return '<Examen {}>'.format(self.status)


#############End Database########################
