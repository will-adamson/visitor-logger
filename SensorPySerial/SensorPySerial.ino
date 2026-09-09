//Pins
const int trigPin = 9;
const int echoPin = 10;
const int threshold = 45;

//Sensor distance
float duration, distance;

//Data capture
bool wasDetected = false;


void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void loop() {

  // BEGIN: https://projecthub.arduino.cc/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-7cabe1
  // The following code is from Arduino Project Hub and is some "getting started" code for the ultrasonic sensor I'm using
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration*.0343)/2;
  // END: https://projecthub.arduino.cc/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-7cabe1

  if(distance < threshold)
  {
    if(!wasDetected){
      int intDistance = static_cast<int>(distance); 
      Serial.println("Dectected,");
      Serial.println(intDistance);
      wasDetected = true;
    }
  }else{
    wasDetected = false;
  }

  delay(100);
}

