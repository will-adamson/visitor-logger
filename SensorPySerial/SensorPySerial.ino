#include <avr/wdt.h> //Watchdog

//Pins
const int trigPin = 9;
const int echoPin = 10;

//Potentiometer detection range (cm)
const int potPin = A0;
const int minRange = 20;
const int maxRange = 100;
const int rangeChangeThreshold = 2; //For ignoring small changes
int detectionRange = 0;

//Timing (ms)
const unsigned long readInterval = 100;
const unsigned long cooldownPeriod = 3000;

unsigned long lastReadTime = 0;
unsigned long lastDetectionTime = 0;
bool wasDetected = false;

//Recent readings, filtered with a median to ignore bad readings
const int sampleCount = 5;
const float noEchoDistance = 500; //pulseIn timed out, so nothing is in range. I'm treating it as far away
float readings[sampleCount];
int readingIndex = 0;

//Pause button
const int buttonPin = 2;
const unsigned long debounceDelay = 400;
volatile bool paused = false;

//Status LED
const int ledPin = 6;
const unsigned long fadePeriod = 2000; //One full fade up and down

//Heartbeat
const unsigned long heartbeatInterval = 1000;
unsigned long lastHeartbeatTime = 0;


void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(buttonPin), onButtonPress, FALLING);
  Serial.begin(9600);

  //Treating first result as far away instead of 0
  for (int i = 0; i < sampleCount; i++) {
    readings[i] = noEchoDistance;
  }

  //Initiate starting range from where the knob is set to
  detectionRange = readRange();
  sendRange();

  //Resets the Arduino if loop() stops running for 2 seconds
  wdt_enable(WDTO_2S);
}

void loop() {
  wdt_reset(); //Resets watchdog timer
  unsigned long now = millis();
  updateLed(now);
  updateRange();
  sendHeartbeat(now);

  if (paused) {
    return;
  }

  if (now - lastReadTime >= readInterval) {
    lastReadTime = now;
    checkForVisitor(medianDistance(readDistance()), now);
  }
}


float readDistance() {
  // BEGIN: https://projecthub.arduino.cc/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-7cabe1
  // The following code is from Arduino Project Hub and is some "getting started" code for the ultrasonic sensor I'm using
  //There was no reason not to use it, works perfectly for my use case and saves me doing it myself
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  float duration = pulseIn(echoPin, HIGH, 30000);
  float distance = (duration*.0343)/2;
  // END: https://projecthub.arduino.cc/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-7cabe1

  if (distance == 0) {
    return noEchoDistance;
  }
  return distance;
}

//Stores the newest reading and returns the median, which ignores occasional bad readings
float medianDistance(float newReading) {
  readings[readingIndex] = newReading;
  readingIndex = (readingIndex + 1) % sampleCount;

  //BEGIN: https://www.geeksforgeeks.org/cpp/cpp-program-for-insertion-sort/
  //Insertion sort
  float sorted[sampleCount];
  for (int i = 0; i < sampleCount; i++) {
    sorted[i] = readings[i];
  }
  for (int i = 1; i < sampleCount; i++) {
    float key = sorted[i];
    int j = i - 1;
    while (j >= 0 && sorted[j] > key) {
      sorted[j + 1] = sorted[j];
      j--;
    }
    sorted[j + 1] = key;
  }
  //END: https://www.geeksforgeeks.org/cpp/cpp-program-for-insertion-sort/
  return sorted[sampleCount / 2];
}

void checkForVisitor(float distance, unsigned long now) {
  bool inRange = distance < detectionRange;
  if (!inRange) {
    wasDetected = false;
    return;
  }

  //Only report a new arrival, and not while cooling down from the last one
  bool coolingDown = now - lastDetectionTime < cooldownPeriod;
  if (!wasDetected && !coolingDown) {
    Serial.print("DETECTED,");
    Serial.println(static_cast<int>(distance));
    lastDetectionTime = now;
  }
  wasDetected = true;
}

//Interrupt when the button pulls pin 2 LOW
void onButtonPress() {
  static unsigned long lastPressTime = 0;
  unsigned long now = millis();

  //Ignore repeats within debounceDelay
  if (now - lastPressTime > debounceDelay) {
    paused = !paused;
    lastPressTime = now;
  }
}

//Slow fade while armed, off while paused
void updateLed(unsigned long now) {
  if (paused) {
    analogWrite(ledPin, 0);
    return;
  }

  unsigned long phase = now % fadePeriod;
  unsigned long half = fadePeriod / 2;
  int brightness = phase < half
    ? map(phase, 0, half, 0, 255)
    : map(phase, half, fadePeriod, 255, 0);
  analogWrite(ledPin, brightness);
}

//Converts the potentiometer position (0-1023) into a detection range in cm
int readRange() {
  return map(analogRead(potPin), 0, 1023, minRange, maxRange);
}

//Only sends a new range when the knob has actually moved
void updateRange() {
  int newRange = readRange();
  if (abs(newRange - detectionRange) >= rangeChangeThreshold) {
    detectionRange = newRange;
    sendRange();
  }
}

void sendRange() {
  Serial.print("RANGE,");
  Serial.println(detectionRange);
}


void sendHeartbeat(unsigned long now) {
  if (now - lastHeartbeatTime >= heartbeatInterval) {
    lastHeartbeatTime = now;
    Serial.println("HEARTBEAT");
  }
}

