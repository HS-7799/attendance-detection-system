import paho.mqtt.client as mqtt
import cv2
import numpy as np
import time
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint, jsonify
from services.models import *
import threading
from flask_login import (
    current_user,
    login_required,
)
import paho.mqtt.client as mqtt
import cv2
import numpy as np
import time

re = Blueprint('re', __name__, template_folder="templates")


@re.route('/recognize', methods=['POST', 'GET'])
# @login_required
def recognize():
    global rfid_detected
    global pir_detected
    global current_uid
    if "examid" and "salleId" in request.args:
        examId = request.args['examId']
        salleId = request.args['salleId']
        users = []
        examen_salle = Examen_Salle.query.filter_by(
            examen_id=examId, salle_id=salleId).one_or_none()
        exam = Examen.query.filter_by(id=examId).first()
        for classe in examen_salle.classes:
            for user_examen in exam.user_examen:
                if user_examen.user.class_id == classe.id:
                    users.append(user_examen)
                    print(user_examen.user.uuid)
    if "uuid" in request.args:
        uuid = request.args['uuid']
        print(uuid)

    # return render_template('admin/recognize.html', current_user=current_user)
    return render_template('graph.html', current_user=current_user)
