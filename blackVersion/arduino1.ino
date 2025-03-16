#include <SoftwareSerial.h>

// Create a software serial object on pins 2 and 3 (for communication with Arduino 2)
SoftwareSerial mySerial(2, 3);  // RX, TX for communication with Arduino 2

const int trigPin1 = 8;
const int echoPin1 = 7;

const long interval = 100;
long lastSent = 0;

bool activate = false

void setup() {
  // Initialize serial communication
  Serial.begin(9600);   // Communication with Computer 1
  mySerial.begin(9600); // Communication with Arduino 2
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
}

void loop() {
  long cm1 = 0, cm2 = 0;
  long timeStart;
  double velocity;

  if (activate) {
    timeStart = millis();
    cm1 = sonarSensor(trigPin1, echoPin1);
    delay(100);
    cm2 = sonarSensor(trigPin1, echoPin1);
    velocity = calcVelocity(cm1, cm2, millis() - timeStart);

    // Send the velocity data to Arduino 2 (via SoftwareSerial)
    mySerial.println(velocity);
  }
    // If there is data from Arduino 1, forward it to Computer 2 (via Serial)
  if (millis() - lastSent > interval)  {
    lastSent = millis();

    if (mySerial.available() > 0) {
      String data = mySerial.readStringUntil('\n');
      Serial.println(data); // Send the data to Computer 2
      Serial.flush();
    }

    // If there is data from Computer 2, forward it to Arduino 1
    if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');
      mySerial.println(data); // Send the data to Arduino 1
      mySerial.flush();
    }
  }

  //delay(50); // Small delay to prevent overwhelming the serial buffers
}

long sonarSensor(int trigPin, int echoPin) {
  long duration;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  return microsecondsToCentimeters(duration);
}

long microsecondsToCentimeters(long microseconds) {
  return microseconds / 29 / 2;
}

double calcVelocity(long cm1, long cm2, long dt) {
  return (cm2 - cm1) / ((double)dt / 1000);
}
