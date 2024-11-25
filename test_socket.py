from flask import Flask
from flask_socketio import SocketIO
import time
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Test WebSocket Server Running"

def emit_control_updates():
    while True:
        socketio.emit('control_updated', {
            'frequency': 50,
            'intensity': 80
        }, namespace='/')
        time.sleep(5)  # Emit every 5 seconds

if __name__ == '__main__':
    thread = Thread(target=emit_control_updates)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
