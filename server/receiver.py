import socket
import cv2
import numpy as np

class FrameProcessor:
    def __init__(self):
        self.latest_frame = None
    
    def set_frame(self, frame):
        self.latest_frame = frame.copy()
    
    def get_frame(self):
        if self.latest_frame is not None:
            return self.latest_frame.copy()
        return None

def process_frame(frame):
    """Apply basic OpenCV processing to frame"""
    processed = frame.copy()
    
    # Add frame info
    height, width = processed.shape[:2]
    cv2.putText(processed, f"Size: {width}x{height}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Apply edge detection
    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Stack original and processed side-by-side
    combined = np.hstack([processed, edges_colored])
    
    return combined

def connect_and_stream(esp32_ip, esp32_port=80):
    """Direct socket connection to ESP32"""
    processor = FrameProcessor()
    
    print(f"Connecting to {esp32_ip}:{esp32_port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((esp32_ip, esp32_port))
        print("✓ Connected!")
        
        # Send HTTP GET request
        http_request = b"GET / HTTP/1.1\r\nHost: " + esp32_ip.encode() + b"\r\nConnection: close\r\n\r\n"
        sock.send(http_request)
        print("✓ HTTP request sent")
        
        bytes_data = b''
        frame_count = 0
        
        print("✓ Display window starting (press 'q' to quit)\n")
        
        while True:

            try:
                print('Loop #1')
                # Receive data in chunks
                chunk = sock.recv(4096)
                
                if not chunk:
                    print("Connection closed")
                    break
                
                bytes_data += chunk
                
                # Find JPEG frame boundaries
                start = bytes_data.find(b'\xff\xd8')
                end = bytes_data.find(b'\xff\xd9')
                
                # print('Loop #1')
                
                if start != -1 and end != -1 and end > start:
                    # Extract complete JPEG frame
                    jpg_data = bytes_data[start:end+2]
                    bytes_data = bytes_data[end+2:]
                    
                    # Decode JPEG
                    nparr = np.frombuffer(jpg_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        frame_count += 1
                        
                        # Process frame
                        processed = process_frame(frame)
                        processor.set_frame(processed)
                        
                        # Display
                        cv2.imshow("ESP32 Stream - Processed", processed)
                        
                        if frame_count % 30 == 0:
                            print(f"✓ Processed {frame_count} frames")
                        
                        # Check for quit key
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            print("Quitting...")
                            break
            
            except KeyboardInterrupt:
                print("Interrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
    
    except socket.error as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()
        cv2.destroyAllWindows()
        print(f"Total frames: {frame_count}")

if __name__ == '__main__':
    esp32_ip = "172.18.200.82"
    connect_and_stream(esp32_ip)