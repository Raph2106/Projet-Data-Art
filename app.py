from flask import Flask, Response
from flask_socketio import SocketIO, emit
from chaleur import generate_frame
import time
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.debug = True

socketio = SocketIO(app)


@app.context_processor
def inject_time():
    return {"time": time.time}


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route('/video_feed')
def video_feed():
    return app.send_static_file("video_feed.html")


@app.route('/test')
def testFlask():
    return Response(response="Réponse de Flask. \n")


@app.route('/video_stream')
def video_stream():
    return Response(generate_frame,
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on("send_data")
def handle_send_data(data):
    print("Données reçues:", data)
    emit("data_response", {"status": "Données reçues avec succès"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=1120)
