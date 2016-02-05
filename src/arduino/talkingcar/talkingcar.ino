// Comment this to use motors
//#define USE_LIGHTS

#define MOTOR_A_DIRECTION   (12)
#define MOTOR_A_PWM         (3)
#define MOTOR_A_BRAKE       (9)
#define MOTOR_A_CURRENT     (0)

#define MOTOR_B_DIRECTION   (13)
#define MOTOR_B_PWM         (11)

#define PROXIMITY_TRIGGER   (2)
#define PROXIMITY_FORWARD   (4)
#define PROXIMITY_BACKWARD  (5)
#define PROXIMITY_RIGHT     (6)
#define PROXIMITY_LEFT      (7)

#define PROXIMITY_FILTER        (0.6)
#define PROXIMITY_DELAY         (30) // Microseconds
#define PROXIMITY_MAX_DISTANCE  (450) // Cm

#define DURATION_TO_CM(duration)  ((duration) / 58.0)
#define CM_TO_DURATION(cm)        ((cm) * 58.0)

#include "DataTypes.h"

void setup() {
  pinMode(PROXIMITY_TRIGGER, OUTPUT);
  pinMode(PROXIMITY_FORWARD, INPUT);
  pinMode(PROXIMITY_BACKWARD, INPUT);
  pinMode(PROXIMITY_RIGHT, INPUT);
  pinMode(PROXIMITY_LEFT, INPUT);
  
  Serial.begin(115200);
  analogWrite(MOTOR_A_PWM, 128);
}

void gas(Gear gear) {
#ifdef USE_LIGHTS
  if (gear == GearForward) {
    digitalWrite(LIGHT_BLUE, 1);
  } else if (gear == GearBackward) {
    digitalWrite(LIGHT_BLUE, 0);
  }
#else
  digitalWrite(MOTOR_A_BRAKE, LOW);
  digitalWrite(MOTOR_A_DIRECTION, static_cast<uint8_t>(gear));
  digitalWrite(MOTOR_A_PWM, HIGH);
#endif
}

void brake() {
#ifdef USE_LIGHTS
  digitalWrite(LIGHT_GREEN, 0);
  digitalWrite(LIGHT_BLUE, 0);
#else
  digitalWrite(MOTOR_A_PWM, LOW);
  digitalWrite(MOTOR_A_BRAKE, HIGH);
#endif
}

void setDirection(Direction direction) {
#ifdef USE_LIGHTS
  if (direction == DirectionRight) {
    digitalWrite(LIGHT_GREEN, 1);
  } else if (direction == DirectionLeft) {
    digitalWrite(LIGHT_GREEN, 0);
  }
#else
  if (DirectionInvalid == direction) {
    digitalWrite(MOTOR_B_PWM, LOW);
  } else {
    digitalWrite(MOTOR_B_DIRECTION, static_cast<uint8_t>(direction));
    digitalWrite(MOTOR_B_PWM, HIGH);
  }
#endif
}

void handleIncomingMessage() {
  CommandHeader header;
  if (Serial.available() < sizeof(header)) {
    return;
  }

  Serial.readBytes((char *) &header, sizeof(header));
  
  if (header.magic != 0xDEADBEEF) {
    return;
  }
  
  if (header.command == CommandGas) {
    GasCommandParams params;
    Serial.readBytes((char *) &params, sizeof(params));
    
    gas(params.gear);
  } else if (header.command == CommandSetDirection) {
    SetDirectionCommandParams params;
    Serial.readBytes((char *) &params, sizeof(params));
    
    setDirection(params.direction);
  } else if (header.command == CommandBrake) {
    brake();
  }
}

int smooth(int data, float filterVal, float smoothedValue) {
  return (int) ((data * (1 - filterVal)) + (smoothedValue  *  filterVal));
}

void triggerProximity() {
  delay(PROXIMITY_DELAY);
  
  digitalWrite(PROXIMITY_TRIGGER, LOW);
  delayMicroseconds(2);
  digitalWrite(PROXIMITY_TRIGGER, HIGH);
  delayMicroseconds(10);
  digitalWrite(PROXIMITY_TRIGGER, LOW);
}

void readProximitySensor(float& duration, int pin) {
  triggerProximity();

  unsigned long pulse = pulseIn(pin, HIGH, 30 * 1000);
  if (0 != pulse) {
    duration = smooth(pulse, PROXIMITY_FILTER, duration);
  } else {
    duration = CM_TO_DURATION(PROXIMITY_MAX_DISTANCE);
  }
}

void sendCarData() {
  // Durations
  static float durationForward = 0;
  static float durationBackward = 0;
  static float durationRight = 0;
  static float durationLeft = 0;

  static uint32_t current = 0;
  current = smooth(analogRead(A0), PROXIMITY_FILTER, current);
  
  // Retrive durations from all proximity sensors
  readProximitySensor(durationForward, PROXIMITY_FORWARD);
  readProximitySensor(durationBackward, PROXIMITY_BACKWARD);
  readProximitySensor(durationRight, PROXIMITY_RIGHT);
  readProximitySensor(durationLeft, PROXIMITY_LEFT);
  
  // Build car state
  CarState carState;
  carState.magic = 0x12345678;
  carState.directionForward = DURATION_TO_CM(durationForward);
  carState.directionBackward = DURATION_TO_CM(durationBackward);
  carState.directionRight = DURATION_TO_CM(durationRight);
  carState.directionLeft = DURATION_TO_CM(durationLeft);
  carState.current = current;
  
  Serial.write((char *) &carState, sizeof(carState));
}

void loop() {
  sendCarData();
  handleIncomingMessage();
}
