#include <SPI.h>
#include <Servo.h>
#include "motor_control.h"
#include "student_functions.h"

void setup() { 
  Serial.begin(9600); //initialising serial connection

  Serial.println("System initialized");
  Serial.println("Commands: s=stop, f=forward, b=backward, l=left, r=right, a=strafe_left, d=strafe_right, o=servo_open, p=servo_close");

  servo_init();
  motor_init();
}

void loop() {
  // Read from Serial instead of WiFi
  if (Serial.available()) {
    char c = Serial.read();
    Serial.write(c);         // Echo back to serial monitor

    //checking if one of standard commands
    if (c == 's') {
      //STOP
      stop();
      Serial.println("Motors Stopped");
    }
    if (c == 'f') {
      //MOVE FORWARD
      //expecting a format of '[power (0-9)] [time (0-9)]'
      char space1 = Serial.read(); //empty space read
      char power = Serial.read();
      char space2 = Serial.read(); //empty space read
      char time = Serial.read();

      String outputmessage = "Going forward at power and time: ";
      outputmessage += power;
      outputmessage += ' ';
      outputmessage += time;
      Serial.println(outputmessage);

      //converting the chars to ints
      int itime = time - '0';
      int ipower = power - '0';

      go_forward(ipower, itime);
    }

    if (c == 'b') {
      //MOVE BACKWARDS
      //expecting a format of '[power (0-9)] [time (0-9)]'
      char space1 = Serial.read(); //empty space read
      char power = Serial.read();
      char space2 = Serial.read(); //empty space read
      char time = Serial.read();

      String outputmessage = "Going backwards at power and time: ";
      outputmessage += power;
      outputmessage += ' ';
      outputmessage += time;
      Serial.println(outputmessage);

      //converting the chars to ints
      int itime = time - '0';
      int ipower = power - '0';

      go_backward(ipower, itime);
    }

    if (c == 'l') {
      //ROTATE LEFT
      //expecting a format of '[power (0-9)] [time (0-9)]'
      char space1 = Serial.read(); //empty space read
      char power = Serial.read();
      char space2 = Serial.read(); //empty space read
      char time = Serial.read();

      String outputmessage = "Rotating left at power and time: ";
      outputmessage += power;
      outputmessage += ' ';
      outputmessage += time;
      Serial.println(outputmessage);

      //converting the chars to ints
      int itime = time - '0';
      int ipower = power - '0';

      turn_left(ipower, itime);
    }

    if (c == 'r') {
      //ROTATE RIGHT
      //expecting a format of '[power (0-9)] [time (0-9)]'
      char space1 = Serial.read(); //empty space read
      char power = Serial.read();
      char space2 = Serial.read(); //empty space read
      char time = Serial.read();

      String outputmessage = "Rotating right at power and time: ";
      outputmessage += power;
      outputmessage += ' ';
      outputmessage += time;
      Serial.println(outputmessage);

      //converting the chars to ints
      int itime = time - '0';
      int ipower = power - '0';

      turn_right(ipower, itime);
    }

    if (c == 'a') {
      //TRANSLATE LEFT
      //expecting a format of '[power (0-9)] [time (0-9)]'
      char space1 = Serial.read(); //empty space read
      char power = Serial.read();
      char space2 = Serial.read(); //empty space read
      char time = Serial.read();

      String outputmessage = "Going left at power and time: ";
      outputmessage += power;
      outputmessage += ' ';
      outputmessage += time;
      Serial.println(outputmessage);

      //converting the chars to ints
      int itime = time - '0';
      int ipower = power - '0';

      translate_left(ipower, itime);
    }

    if (c == 'd') {
      //TRANSLATE RIGHT
      //expecting a format of '[power (0-9)] [time (0-9)]'
      char space1 = Serial.read(); //empty space read
      char power = Serial.read();
      char space2 = Serial.read(); //empty space read
      char time = Serial.read();

      String outputmessage = "Going right at power and time: ";
      outputmessage += power;
      outputmessage += ' ';
      outputmessage += time;
      Serial.println(outputmessage);

      //converting the chars to ints
      int itime = time - '0';
      int ipower = power - '0';

      translate_right(ipower, itime);
    }

    // === SAMPLE SERVO CONTROL ===
    if (c == 'o') {
      servo_open();
      Serial.println("O function triggered");
    }
    if (c == 'p') {
      servo_close();
      Serial.println("P function triggered");
    }

    if (c == 'u') {
      // Reserved for future use
    }
  }
}
