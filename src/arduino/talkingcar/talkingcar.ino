#include <ESP8266wifi.h>

// Comment this to use motors
#define USE_LIGHTS

#define LIGHT_BLUE          (7)
#define LIGHT_GREEN         (8)

#define MOTOR_A_DIRECTION   (12)
#define MOTOR_A_PWM         (3)
#define MOTOR_A_BRAKE       (9)

#define MOTOR_B_DIRECTION   (13)
#define MOTOR_B_PWM         (11)

#pragma pack(push, 1)

/* Command header */
typedef enum Command {
  CommandInvalid = -1,
  CommandGas = 0,
  CommandBrake = 1,
  CommandSetDirection = 2
} Command;

typedef struct _CommandHeader {
  uint32_t magic;
  Command command;
} CommandHeader;

/* Gas command */
typedef enum _Gear {
  GearInvalid = -1,
  GearForward = 0,
  GearBackward = 1  
} Gear;

typedef struct _GasCommandParams {
  Gear gear;
} GasCommandParams;

/* SetDirection command */
typedef enum _Direction {
  DirectionInvalid = -1,
  DirectionLeft = 1, 
  DirectionRight = 0 
} Direction;

typedef struct _SetDirectionCommandParams {
  Direction direction;
} SetDirectionCommandParams;

#pragma pack(pop)

ESP8266wifi wifi(Serial, Serial, 10);

void setup() {
  pinMode(LIGHT_BLUE, OUTPUT);
  pinMode(LIGHT_GREEN, OUTPUT);

  initWifi();
}

void initWifi() {
  Serial.begin(115200);
 
  wifi.setTransportToTCP();
  wifi.endSendWithNewline(true);

  while (!wifi.isStarted()) {
    wifi.begin();
  }
  
  wifi.startLocalAPAndServer("TalkingCar", "password", "5", "8763");
}

void loop() {
  WifiMessage in = wifi.listenForIncomingMessage(6000);
  if (in.hasData) {
    handleMessage(in.message);
  }
}

void handleMessage(const char * message) {
  CommandHeader* header = (CommandHeader*) message;
  if (header->magic != 0xDEADBEEF) {
    return;
  }
  
  if (header->command == CommandGas) {
    GasCommandParams* params = (GasCommandParams*) ((char *) header + sizeof(CommandHeader));
    gas(params->gear);
  } else if (header->command == CommandSetDirection) {
    SetDirectionCommandParams* params = (SetDirectionCommandParams*) ((char *) header + sizeof(CommandHeader));
    setDirection(params->direction);
  } else if (header->command == CommandBrake) {
    brake();
  }
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

