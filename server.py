from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)


@app.context_processor
def inject_time():
    return {"time": time.time}


@app.route("/")
def index():
    return app.send_static_file("index.html")


@socketio.on("send_data")
def handle_send_data(data):
    print("Données reçues:", data)
    emit("data_response", {"status": "Données reçues avec succès"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=1020)
