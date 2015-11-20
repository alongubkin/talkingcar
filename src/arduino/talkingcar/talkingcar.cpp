#define MOTOR_A_DIRECTION 12
#define MOTOR_A_PWM 3
#define MOTOR_A_BRAKE 9

#define MOTOR_B_DIRECTION 13
#define MOTOR_B_PWM 11

enum Gear
{
  GearForward = LOW,
  GearBackward = HIGH
};

enum Direction
{
  DirectionNone = 50,  
  DirectionRight = HIGH,
  DirectionLeft = LOW
};

class Car 
{
public:
  Car() = default;
  virtual ~Car() = default;
  Car(const Car&) = delete;  
  Car& operator=(const Car&) = delete;

  void gas(Gear gear);  
  void brake();

  void setDirection(Direction direction);
};

void Car::gas(Gear gear)
{
  digitalWrite(MOTOR_A_BRAKE, LOW);
  digitalWrite(MOTOR_A_DIRECTION, static_cast<uint8_t>(gear));
  digitalWrite(MOTOR_A_PWM, HIGH);
}

void Car::brake()
{
  digitalWrite(MOTOR_A_PWM, LOW);
  digitalWrite(MOTOR_A_BRAKE, HIGH);
}

void Car::setDirection(Direction direction)
{
  if (DirectionNone == direction)
  {
    digitalWrite(MOTOR_B_PWM, LOW);
  }
  else
  {
    digitalWrite(MOTOR_B_DIRECTION, static_cast<uint8_t>(direction));
    digitalWrite(MOTOR_B_PWM, HIGH);
  }
}

Car car;

void setup()
{
  
  pinMode(MOTOR_A_DIRECTION, OUTPUT);
  pinMode(MOTOR_A_PWM, OUTPUT);
  pinMode(MOTOR_A_BRAKE, OUTPUT);
  
  pinMode(MOTOR_B_DIRECTION, OUTPUT);
  pinMode(MOTOR_B_PWM, OUTPUT);
  
}

void loop()
{
  car.gas(GearForward);
  delay(500);

  car.setDirection(DirectionRight);
  delay(250);

  car.setDirection(DirectionNone);
  delay(250);

  car.setDirection(DirectionLeft);
  delay(250);

  car.setDirection(DirectionNone);
  delay(250);
    
  car.brake();
  delay(5000);
  
}
