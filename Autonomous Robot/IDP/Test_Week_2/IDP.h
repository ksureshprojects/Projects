//
//  IDP.h
//  
//
//  Created by Admin on 12/10/17.
//
//

#ifndef IDP_h
#define IDP_h

#define ROBOT_NUM 3

#define NORTH 0
#define EAST 1
#define SOUTH 2
#define WEST 3

#define RIGHT 1 // Corresponds to R and L motor
#define LEFT 2
#define DROP 0
#define PICK 3

#define SPEED 100

#define CRL 255
#define C 249
#define CL 251
#define CR 253
#define RL 254
#define NONE 248
#define L 250
#define R 252
// Red is Motor 1 (L) is goofy
// Green is Motor 2 (R)

// Global Variables

extern int orientation;
//extern junction current; // Current junction
//extern junction next; // Junction to travel to next
extern int IR; //Binary IR sensor data
extern int junction_counter;

int front_veering()
//int back_veering();
//int turn_checking();
void right_turn()
void left_turn()
void execute_action(int action)
void travel(int ** path)

#endif /* IDP_h */
