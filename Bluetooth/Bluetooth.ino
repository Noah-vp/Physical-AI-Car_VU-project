#include "BluetoothSerial.h"
#include <HardwareSerial.h>

// Create a BluetoothSerial object
BluetoothSerial SerialBT;
HardwareSerial NanoSerial(1);

void setup() {
  Serial.begin(115200); // Debugging via Serial Monitor
  NanoSerial.begin(9600, SERIAL_8N1, 18, 19); // Assuming RX=18, TX=19
  SerialBT.begin("ESP32_BT"); // Initialize Bluetooth with the device name
  Serial.println("Bluetooth device is ready to pair.");
}

void loop() {
  if (SerialBT.available()) { // Check if data is available
    String incomingString = SerialBT.readStringUntil('\n'); // Read until newline
    Serial.print("Received string: ");
    Serial.println(incomingString); // Print to Serial Monitor
    NanoSerial.println(incomingString);
    Serial.println("String send.");
  }
}
