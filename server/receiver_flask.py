import cv2
import numpy as np
import socket
import threading
from flask import Flask, render_template_string, Response

app = Flask(__name__)

class CameraStream:
    def __init__(self, esp32_ip):
        self.esp32_ip = esp32_ip
        self.latest_frame = None
        self.sock = None
        self.running = False
    
    def connect(self):
        """Connect to ESP32 and stream frames"""
        print(f"Connecting to {self.esp32_ip}:80")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.esp32_ip, 80))
            print("✓ Connected to ESP32!")
            
            # Send HTTP GET request
            http_request = b"GET / HTTP/1.1\r\nHost: " + self.esp32_ip.encode() + b"\r\nConnection: close\r\n\r\n"
            self.sock.send(http_request)
            print("✓ HTTP request sent")
            
            bytes_data = b''
            frame_count = 0
            self.running = True
            
            while self.running:
                try:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        print("Connection closed")
                        break
                    
                    bytes_data += chunk
                    
                    # Find JPEG frame boundaries
                    start = bytes_data.find(b'\xff\xd8')
                    end = bytes_data.find(b'\xff\xd9')
                    
                    if start != -1 and end != -1 and end > start:
                        jpg_data = bytes_data[start:end+2]
                        bytes_data = bytes_data[end+2:]
                        
                        nparr = np.frombuffer(jpg_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            frame_count += 1
                            self.latest_frame = frame
                            
                            if frame_count % 30 == 0:
                                print(f"✓ Processed {frame_count} frames")
                
                except Exception as e:
                    print(f"Error reading frame: {e}")
                    break
        
        except socket.error as e:
            print(f"Connection error: {e}")
        finally:
            if self.sock:
                self.sock.close()
            self.running = False
    
    def get_frame(self):
        """Get latest frame as JPEG bytes for streaming"""
        if self.latest_frame is None:
            return None
        
        ret, buffer = cv2.imencode('.jpg', self.latest_frame)
        return buffer.tobytes() if ret else None

# Initialize camera stream
camera = CameraStream("172.18.200.82")

@app.route('/')
def index():
    """Serve the web interface"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Camera Stream</title>
        <style>
            body {
                font-family: Arial;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background-color: #1a1a1a;
                color: white;
            }
            .container {
                text-align: center;
                background-color: #2d2d2d;
                padding: 20px;
                border-radius: 10px;
            }
            h1 { color: #4CAF50; }
            img { 
                max-width: 100%;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 Camera Stream</h1>
            <img src="/stream" alt="Live Stream">
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/stream')
def stream():
    """Stream video frames"""
    def generate():
        while True:
            frame_bytes = camera.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                       + frame_bytes + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_camera_thread():
    """Start camera stream in background thread"""
    thread = threading.Thread(target=camera.connect, daemon=True)
    thread.start()

if __name__ == '__main__':
    print("Starting Flask server...\n")
    
    # Start camera stream in background
    start_camera_thread()
    
    # Run Flask server
    print("✓ Flask server running on http://localhost:5000")
    print("✓ Open http://localhost:5000 in your browser\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)