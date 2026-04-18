from flask import Flask, Response, request
import cv2
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so the static InsForge frontend can connect without Cross-Origin issues
CORS(app)

# Credentials and IP should be passed via env vars, but hardcoded here for the demo adaptation
# WARNING: Do not commit sensitive credentials inside Docker images in production.
RTSP_USER = "admin"
RTSP_PASS = "admin123"
RTSP_IP = "61.13.222.78:8080"
RTSP_URL = f"rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP}/cam/realmonitor?channel=1&subtype=0"

def generate_frames():
    # Attempt to open the video stream
    camera = cv2.VideoCapture(RTSP_URL)
    if not camera.isOpened():
        print("Failed to open RTSP stream")
        return

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Resize frame to save bandwidth over HTTP
            frame = cv2.resize(frame, (640, 360))
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Yield the frame in byte format for MJPEG stream multipart
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def health_check():
    return "RTSP Proxy is running!"

@app.route('/stream')
def video_feed():
    # Return the response generated along with the specific multimedia type
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Internal port generally mapped appropriately by Docker / Fly.io defaults to 8080
    app.run(host='0.0.0.0', port=8080)
