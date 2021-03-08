import eventlet
import sys
import cv2
from time import gmtime, strftime
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from services.models import *
import numpy as np

app = Flask(__name__)
eventlet.monkey_patch()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bajit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MQTT_BROKER_URL'] = '192.168.43.176'
app.config['MQTT_USERNAME'] = 'pi'
app.config['MQTT_PASSWORD'] = '123456'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0
db.init_app(app)
mqtt = Mqtt(app)
socketio = SocketIO(app)
pir = 0
rfid = 0


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("/esp32/1/pir")
    mqtt.subscribe("/esp8266/1/rfid")
    mqtt.subscribe("/esp32/1/cam")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    if message.topic == "/esp32/1/pir":
        if int(message.payload) == 1:
            data = dict(
                topic=message.topic,
                payload="okpir"
            )
            socketio.emit('mqtt_message', data=data)
            global pir
            pir = 1
    if message.topic == "/esp8266/1/rfid" and pir == 1:
        with app.app_context():
            exam = Examen.query.filter_by(id=1).first()
            for user_examen in exam.user_examen:
                uuid = str(message.payload.decode()).replace(' ', '')
                if user_examen.user.uuid == uuid:
                    user_examen.etat = 1
                    user_examen.start = strftime("%H:%M:%S", gmtime())
                    rfid = 1
                    db.session.commit()
                    ret = mqtt.publish("/esp32/1/takeCam", "whatever you want")
                    print(ret)
                    pir = 0
                    break
                else:
                    pir = 0
                    rfid = -1
            if rfid == 1:
                data = dict(
                    topic=message.topic,
                    payload="okrfid"
                )
                socketio.emit('mqtt_message', data=data)
            elif rfid == -1:
                data = dict(
                    topic=message.topic,
                    payload="not authorized"
                )
                socketio.emit('mqtt_message', data=data)
    if message.topic == "/esp32/1/cam":

        buff = []
        print("message received ")
        while True:
            buff = message.payload
            nparr = np.frombuffer(buff, np.uint8)
            img = cv2.imdecode(nparr, 1)
            cv2.imshow('Demo', img)
            cv2.waitKey(1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


@ app.route('/')
def index():
    return render_template('graph.html')


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


socketio.run(app, host='localhost', port=5001, use_reloader=True, debug=True)
