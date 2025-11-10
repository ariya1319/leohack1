// Define the pins for Trigger and Echo
const int trigPin = 9;
const int echoPin = 10;


void setup() {
  // Start serial communication

  Serial.begin(9600);
  
  // Set the trigger pin as output and echo pin as input
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

}

void loop() {
  // Send a pulse to trigger the ultrasonic sensor
  digitalWrite(trigPin, LOW);  // Ensure trigPin is LOW before sending HIGH
  delayMicroseconds(2);        // Wait for 2 ms
  
  digitalWrite(trigPin, HIGH); // Send the trigger pulse
  delayMicroseconds(10);       // Keep the pulse HIGH for 10 ms
  digitalWrite(trigPin, LOW);  // End the pulse
  
  // Measure the duration of the pulse on the echo pin
  long duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance in centimeters (speed of sound is 343 m/s or 0.0343 cm/us)
  long distance = duration * 0.0343 / 2;  // Divide by 2 because the pulse travels to the object and back
  
  // Print the distance to the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  
  // Wait for a short time before measuring again
  delay(500);
}
