import json
from services.forms import *
from dotenv import load_dotenv
import os
from flask import Flask, url_for, render_template, request, redirect, session
from services.models import *
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin,
)
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from routes.modules import m
from routes.auth import auth
from routes.rooms import r
from routes.branches import b
from routes.semesters import s
from routes.classes import c
from routes.users import u
from routes.exams import e
from routes.recognize import re
from datetime import date, datetime
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
# dotenv setup required to get or post data in .env


today = date.today().strftime("%Y-%m-%d")

load_dotenv()
# Configuration
# Flask app setup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bajit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MQTT_BROKER_URL'] = "broker.hivemq.com"
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0
db.init_app(app)
app.register_blueprint(m)
app.register_blueprint(r)
app.register_blueprint(b)
app.register_blueprint(s)
app.register_blueprint(c)
app.register_blueprint(u)
app.register_blueprint(e)
app.register_blueprint(re)
login_manager = LoginManager()
login_manager.init_app(app)
app.register_blueprint(auth)
app.secret_key = "hddddddddddddddddddddddddddddsnnaniwoellejdhhqqlodjjdojfihq11222339mdbfHsjkajbduuoqps"


@app.login_manager.unauthorized_handler
def unauth_handler():
    if request.is_xhr:
        return jsonify(success=False,
                       data={'login_required': True},
                       message='Authorize please to access this page.'), 401
    else:
        return render_template("error.html", name='ADMIN', error=401)


@app.route('/home')
def home():
    return render_template("base.html", current_user=current_user)


@app.route('/')
def index():
    return render_template("base.html")


@app.route('/student')
@login_required
def student():
    if (current_user.roles[0].id == 4):
        exams = []
        modules = []
        status = []
        colors = []
        k = 0
        for user_examen in current_user.user_examen:
            # exams.append(current_user.user_examen[0])
            examen = Examen.query.filter_by(
                id=current_user.user_examen[k].examen_id).first()
            k = k+1
            if(examen.date > datetime.strptime(today, '%Y-%m-%d').date()):
                status.append('Not Yet')
                colors.append(0)
            else:
                if(examen.status == 1):
                    status.append("You were present")
                    colors.append(1)
                else:
                    status.append("You were absent")
                    colors.append(2)
            exams.append(examen)
            modules.append(Module.query.filter_by(id=examen.module_id).first())
        return render_template("/student/index.html", current_user=current_user, examens=exams, modules=modules, status=status, colors=colors)
    else:
        return render_template("error.html", name='ENSAKISTE', error=404)


if __name__ == "__main__":
    app.run(host='localhost', port=5000, use_reloader=True, debug=True)
