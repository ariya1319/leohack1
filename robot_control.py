import time
import serial

class SatelliteRobot:
    def __init__(self):
        """Initialise the satellite robot controller"""
        self.qr_code_threshold = 4
        
        self.arduino = serial.Serial('COM7', 9600, timeout=1)  # Change COM3 to your port
        print(self.arduino.port)
        time.sleep(2)

    def send_command(self, command, power, duration):
        """
        Send movement command to the robot

        Args:
            command (str): Movement command ('w', 's', 'q', 'e')
            power (int): Motor power level (1-9)
            duration (int): Time duration (1-8)
        """

        if power < 1 or power > 9:
            raise ValueError("Power must be between 1 and 9")
        
        if duration < 1 or duration > 8:
            raise ValueError("Duration must be between 1 and 8")
        
        if command not in ['w', 's', 'q', 'e']:
            raise ValueError("Command must be 'w', 's', 'q', or 'e'")
        
        self.arduino.write(command)
        print(f"Command: {command}, Power: {power}, Duration: {duration}")

        time.sleep(0.5)

        while self.arduino.in_waiting:
            print(self.arduino.readline().decode('utf-8').strip())
    
        time.sleep(duration * 0.1)

    def move_forward(self, power=5, duration=3):
        """Move robot forward"""

        self.send_command('w', power, duration)

    def move_backward(self, power=5, duration=3):
        """Move robot backward"""

        self.send_command('s', power, duration)

    def rotate_left(self, power=5, duration=2):
        """Rotate robot left"""

        self.send_command('q', power, duration)

    def rotate_right(self, power=5, duration=2):
        """Rotate robot right"""

        self.send_command('e', power, duration)

    def detect_qr_codes(self):
        """
        Detect QR codes using camera
        
        Returns:
            int: Number of QR codes detected
        """
        qr_count = 0

        print(f"QR codes detected: {qr_count}")

        return qr_count

    def initial_rotation(self, degrees=45, power=5):
        """
        Perform initial rotation
        
        Args:
            degrees (int): Degrees to rotate (positive = left, negative = right)
            power (int): Motor power level
        """

        duration = max (1, min(8, abs(degrees) // 20))

        if degrees > 0:
            print(f"Initial rotation: {degrees} degrees left")
            self.rotate_left(power, duration)
        else:
            print(f"Initial rotation: {abs(degrees)} degrees right")
            self.rotate_right(power, duration)

    def approach_target(self, max_attempts=100):
        """
        Main approach sequence: rotate until 4 QR codes detected, then move forward
        
        Args:
            max_attempts (int): Maximum rotation attempts before giving up
        """

        print("Starting approach sequence...")

        self.initial_rotation(45, power=5)

        attempt = 0
        while attempt < max_attempts:
            print(f"\n--- Attempt {attempt + 1} ---")

            qr_count = self.detect_qr_codes()

            if qr_count >= self.qr_code_threshold:
                print(f"{qr_count} QR codes detected! Moving forward...")
                self.move_forward(power=6, duration=4)
                time.sleep(0.5)
            else:
                print(f"Only {qr_count} QR codes detected. Rotating left...")
                self.rotate_left(power=4, duration=2)
                time.sleep(0.3)

            attempt += 1

if __name__ == '__main__':
    robot = SatelliteRobot()
    robot.move_backward()
