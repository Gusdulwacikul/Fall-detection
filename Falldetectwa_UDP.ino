#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <MPU6050.h>
#include <Callmebot_ESP8266.h>

// MPU6050
MPU6050 mpu;

// WiFi credentials
const char* ssid = "Gusdul Wah";
const char* password = "Gustawacika";

// Destination IP and port for UDP
const IPAddress destinationIP(192, 168, 43, 85);  // IP address of the Python program
const unsigned int destinationPort = 8888;  // Port number of the Python program

WiFiUDP udp;

// Fall detection parameters
const float g = 9.81; // Gravitational acceleration in m/s^2
const float fallThreshold = 1.5 * g; // Threshold for fall detection in m/s^2

// WhatsApp details
String phoneNumber = "+6281235284339";
String apiKey = "8615470";

// Gyroscope and accelerometer variables
float RateRoll, RatePitch, RateYaw;
float AccX, AccY, AccZ;
float AngleRoll, AnglePitch;

void setup() {
  Serial.begin(115200);
  
  // Initialize MPU6050
  Wire.begin();
  mpu.initialize();
  Serial.println("MPU6050 initialized");

  // Connect to WiFi
  connectToWiFi();

  // Initialize Callmebot library
  Callmebot.begin();

  // Initialize UDP
  udp.begin(8266);
  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), 8266);

  // MPU6050 additional setup
  Wire.beginTransmission(0x68); 
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();
}

void loop() {
  // Get gyro and accelerometer signals
  gyro_signals();

  // Convert accelerometer data to strings
  String accelXString = String(AccX, 1);
  String accelYString = String(AccY, 1);
  String accelZString = String(AccZ, 1);

  Serial.print("Accel X: ");
  Serial.println(accelXString);
  Serial.print("Accel Y: ");
  Serial.println(accelYString);
  Serial.print("Accel Z: ");
  Serial.println(accelZString);

  String data = accelXString + "," + accelYString + "," + accelZString;

  // Send UDP packet
  udp.beginPacket(destinationIP, destinationPort);
  udp.write(data.c_str());
  udp.endPacket();

  Serial.println("Data sent: " + data);

  // Fall detection logic
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  // Convert raw accelerometer data to units of g (gravitational acceleration)
  float accelX = ax / 16384.0;
  float accelY = ay / 16384.0;
  float accelZ = az / 16384.0;

  // Convert acceleration from g to m/s^2
  float accelX_mps2 = accelX * g;
  float accelY_mps2 = accelY * g;
  float accelZ_mps2 = accelZ * g;

  Serial.print("Acceleration (m/s^2): ");
  Serial.print("X = ");
  Serial.print(accelX_mps2);
  Serial.print(" m/s^2, Y = ");
  Serial.print(accelY_mps2);
  Serial.print(" m/s^2, Z = ");
  Serial.println(accelZ_mps2);

  // Check for fall detection
  if (detectFall(accelX_mps2, accelY_mps2, accelZ_mps2)) {
    Serial.println("Fall detected!");
    // Send WhatsApp message on fall detection
    sendWhatsAppMessage("Terdeteksi Jatuh !!");
  }

  delay(10);
}

// Function to detect a fall based on acceleration values
bool detectFall(float x, float y, float z) {
  // Check if any of the acceleration values exceed the fall threshold
  if (abs(x) > fallThreshold || abs(y) > fallThreshold || abs(z) > fallThreshold) {
    return true;
  }
  return false;
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void sendWhatsAppMessage(String message) {
  Serial.println("Sending WhatsApp message...");

  Callmebot.whatsappMessage(phoneNumber, apiKey, message);
  Serial.println(Callmebot.debug());

  Serial.println("WhatsApp message sent!");
}

void gyro_signals(void) {
  Wire.beginTransmission(0x68);
  Wire.write(0x1A);
  Wire.write(0x05);
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x10);
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission(); 
  Wire.requestFrom(0x68,6);
  int16_t AccXLSB = Wire.read() << 8 | Wire.read();
  int16_t AccYLSB = Wire.read() << 8 | Wire.read();
  int16_t AccZLSB = Wire.read() << 8 | Wire.read();
  Wire.beginTransmission(0x68);
  Wire.write(0x1B); 
  Wire.write(0x8);
  Wire.endTransmission();                                                   
  Wire.beginTransmission(0x68);
  Wire.write(0x43);
  Wire.endTransmission();
  Wire.requestFrom(0x68,6);
  int16_t GyroX=Wire.read()<<8 | Wire.read();
  int16_t GyroY=Wire.read()<<8 | Wire.read();
  int16_t GyroZ=Wire.read()<<8 | Wire.read();
  RateRoll=(float)GyroX/65.5;
  RatePitch=(float)GyroY/65.5;
  RateYaw=(float)GyroZ/65.5;
  AccX=(float)AccXLSB/4096;
  AccY=(float)AccYLSB/4096;
  AccZ=(float)AccZLSB/4096;
  AngleRoll=atan(AccY/sqrt(AccX*AccX+AccZ*AccZ))*1/(3.142/180);
  AnglePitch=-atan(AccX/sqrt(AccY*AccY+AccZ*AccZ))*1/(3.142/180);
}
