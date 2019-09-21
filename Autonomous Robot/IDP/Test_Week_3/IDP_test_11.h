//
//  IDP_test.h
//  
//
//  Created by Admin on 12/10/17.
//
//

#ifndef IDP_test_h
#define IDP_test_h

#define ROBOT_NUM 3

#define NORTH 0
#define EAST 1
#define SOUTH 2
#define WEST 3

#define LEFT 1 
#define RIGHT 2
#define DROP 3
#define PICK 4

#define SPEED 80

#define CRL 255
#define C 249
#define CL 251
#define CR 253
#define RL 254
#define NONE 248
#define L 250
#define R 252

#define YELH 4
#define WHIH 2
#define MULT 5
#define WHIL 1
#define YELL 3
#define NOD1 3
#define NOD2 2
#define NOD3 1
#define NODR 4

// Red is Motor 1 (L) is goofy
// Green is Motor 2 (R) 

// Global Variables
extern robot_link  rlink; // datatype for the robot link
extern int junction_counter;
extern int critical_junction;
extern int IR; // To record sensor data
extern int IR1; // To record last change in reading
extern int crit; // To signify when critical junction reached
extern int next_node; // used by find_path function
extern int current_node; // used by find_path function
extern int balls_array[6]; // To store the balls data
extern int ballcount;
extern int orientation;

void junction_checker();
void straight_path();
void left_turn();
void right_turn();
void pick_up();
void drop_off();
void path_interpret(vector <vector <int> > path);
void ori(int change);
vector <vector <int> > path_finder(int balls_array[6]);
int ball_type(int weightswitch, int colour);


#endif /* IDP_h */
