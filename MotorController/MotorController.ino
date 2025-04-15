#include <SoftwareSerial.h>

// Define motor pins
int enA = 9;
int in1 = 8;
int in2 = 7;
int enB = 3;
int in3 = 5;
int in4 = 4;

// Define SoftwareSerial pins
int rxPin = 10; // SoftwareSerial RX pin
int txPin = 11; // SoftwareSerial TX pin

// Create a SoftwareSerial object
SoftwareSerial mySerial(rxPin, txPin);

void setup() {
  // Set motor pins as outputs
  pinMode(enA, OUTPUT);
	pinMode(enB, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  // Start SoftwareSerial at 9600 baud
  mySerial.begin(9600);

  // Optional: Start hardware serial for debugging
  Serial.begin(9600);
  Serial.println("Ready to receive commands...");
}

void loop() {
  // Check if a command is available from SoftwareSerial
  if (mySerial.available() > 0) {
    String command = mySerial.readStringUntil('\n'); // Read until newline
    // Trim any extra whitespace or newline characters
    command.trim();
    String direction = command.substring(0,1);
    int speed = getValue(command, ',', 1).toInt();
    Serial.println("Command: " + direction + " | Speed: " + speed);
    handleCommand(direction, speed);
  }
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read until newline
    // Trim any extra whitespace or newline characters
    command.trim();
    String direction = command.substring(0,1);
    int speed = getValue(command, ',', 1).toInt();
    Serial.println("Command: " + direction + " | Speed: " + speed);
    handleCommand(direction, speed);
  }
}

void handleCommand(String command, int speed){
  // Handle commands
    if (command == "L" || command == "l") {  // Left motor
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      analogWrite(enB, speed);
      analogWrite(enA, 255);
      mySerial.println("Left motor on");
      Serial.println("Left motor on (debug)");
    } else if (command == "R" || command == "r") {  // Right motor
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      analogWrite(enA, speed);
      analogWrite(enB, 255);
      mySerial.println("Right motor on");
      Serial.println("Right motor on (debug)");
    } else if (command == "F" || command == "f") {  // Both motors forward
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      analogWrite(enB, 255);
      analogWrite(enA, 255);
      mySerial.println("Both motors forward");
      Serial.println("Both motors forward (debug)");
    } else if (command == "S" || command == "s") {  // Stop
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);
      digitalWrite(in4, LOW);
      mySerial.println("Motors Stopped");
      Serial.println("Motors Stopped (debug)");
    } else {
      // Ignore unknown commands
      mySerial.println("Invalid command");
      Serial.println("Invalid command (debug)");
    }
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}
