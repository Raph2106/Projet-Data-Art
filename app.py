from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit
from chaleur import generate_frame, generate_frame2
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
    return Response(generate_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on("send_data")
def handle_send_data(data):
    print("Données reçues:", data)
    emit("data_response", {"status": "Données reçues avec succès"})


@socketio.on('start_video')
def start_video():
    for frame_base64 in generate_frame2():
        emit('new_frame', {'image': frame_base64})
        time.sleep(0.04)


if __name__ == "__main__":
    socketio.run(app, host="::1",
                 port=1120,
                 ssl_context=("cert.pem", "key.pem"))
