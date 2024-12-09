from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from chaleur import generate_frame
import time
import logging
import threading

logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.debug = True

CORS(app, origins=['https://fenouil.aioli.ec-m.fr'])

socketio = SocketIO(app)

shared_data = {}
data_lock = threading.Lock()


@app.context_processor
def inject_time():
    return {"time": time.time}


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/video_feed')
def video_feed():
    return render_template("video_feed.html")


@app.route('/video_socket')
def video_socket():
    return render_template("video_socket.html")


@app.route('/test')
def testFlask():
    return Response(response="Réponse de Flask. \n")


@app.route('/video_stream')
def video_stream():
    global shared_data
    with data_lock:
        print("Etat de shared_data avant passage en fonction generate_frame :", shared_data)
        return Response(generate_frame(shared_data),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on("send_data")
def handle_send_data(data):
    global shared_data
    with data_lock:
        shared_data = data
    print("Données reçues:", data)
    emit("data_response", {"status": "Données reçues avec succès"})


@socketio.on('start_video')
def start_video():
    for frame_base64 in generate_frame():
        emit('new_frame', {'image': frame_base64})
        time.sleep(0.04)


if __name__ == "__main__":
    socketio.run(app, host="::1",
                 port=1120)
