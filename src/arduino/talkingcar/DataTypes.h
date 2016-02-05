#ifndef _H_DATATYPES
#define _H_DATATYPES
        
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


typedef struct _CarState {
  uint32_t magic;
  float directionForward;
  float directionBackward;
  float directionRight;
  float directionLeft;
  uint32_t current;
} CarState;

#pragma pack(pop)
#endif
