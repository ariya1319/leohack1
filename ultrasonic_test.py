import socket
import time

# ARDUINO_IP = "192.168.4.1"
ARDUINO_IP = "172.18.200.82"
ARDUINO_PORT = 8080

print("Connecting to Arduino...")

try:
    s = socket.socket()
    s.settimeout(5)
    s.connect((ARDUINO_IP, ARDUINO_PORT))
    print("Connected!")
    
    print("\nReading ultrasonic sensor data...")
    print("Press Ctrl+C to exit\n")
    
    while True:
        # Send 'u' command to request ultrasonic reading
        command = 'f'
        s.send(command.encode())
        
        # Wait for Arduino to process and respond
        time.sleep(0.1)
        
        # Receive the response
        try:
            data = s.recv(1024).decode('utf-8').strip()
            
            if data:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] Distance: {data}")
            else:
                print("No data received")
        except socket.timeout:
            print("Timeout waiting for response")
        
        # Wait before next reading
        time.sleep(0.5)
    
except KeyboardInterrupt:
    print("\n\nExiting...")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 's' in locals():
        s.close()
        print("Connection closed")