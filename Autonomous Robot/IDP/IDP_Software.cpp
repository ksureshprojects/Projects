//
//  IDP_Functions.cpp
//
//
//  Created by Admin on 10/10/17.
//
//

#include <stdio.h>
#include "stopwatch.h"
#include "delay.h"

#define NORTH 0
#define EAST 1
#define SOUTH 2
#define WEST 3
#define BLACK 0
#define WHITE 1
#define RIGHT 1 // Corresponds to R and L motor
#define LEFT 2
#define DROP 0
#define PICK 3
#define SPEED 100

// Global Variables

int orientation;
junction current; // Current junction
junction next; // Junction to travel to next
int R, L, C; //Binary IR sensor data

// Functions


/**
 * Travel is a function that moves robot along a given path.
 * Path is an array of two-element arrays that store number of junctions till next action and
 * code for next action to be executed.
 */

int path[3][2] =

void travel(int ** path)
{
    // To count junctions passed and stage in path.
    int junction_counter = 0;
    int path_step = 0;
    int try_counter = 0; // For 3rd troubleshooting case

    
    
    if (path[path_step][0] != 0)
    {
        rlink.command(rlink.command(BOTH_MOTORS_GO_SAME, SPEED);
        delay (1000);
    }
                      
    while(true)
    {
        R, L, C = rlink.request('Binary IR Sensor Data');
        
        if((R == 1 and L == 0) or (R == 0 and L == 1)) // Front veering
        {
            R, L, C = front_veering();
        }
        
        if(C == 0) // Back out of alignment
        {
            R, L, C = back_veering();
        }
        
        if (L == 1 and R == 1 and path[path_step][0] == 0) // action to be executed on current position
        {
            execute_action(path[path_step][1]); // Call execute action function
            path_step ++; // Move to next stage of path
            if (path_step == sizeof(path)/(2*sizeof(int))) // End function if end of path
            {
                break;
            }
        }
        else if (L == 1 and R == 1) // Junction passed
        {
            junction_counter++;
        }
        
        if(junction_counter == path[path_step][0]) // Critical jucntion reached
        {
            rlink.command(rlink.command(MOTOR_2_GO, 0); // L Motor Stop
            rlink.command(rlink.command(MOTOR_1_GO, 0); // R Motor Stop
            execute_action(path[path_step][1]); // Call execute action function
            path_step ++;
            if (path_step == sizeof(path)/(2*sizeof(int))) // End function if end of path
            {
                break;
            }
        }
        
        

    }
}
                          
void execute_action(int action)
{
    switch(action)
    {
        case LEFT : left_turn();
                    break;
        case RIGHT : right_turn();
                     break;
        case DROP : drop_ball();
                    break;
        case PICK : pick_up_ball();
                    break;
    }
}

void right_turn()
{
    R, L, C = rlink.request('Binary IR Sensor Data');
    
    int turn_complete = 0;
    
    if(L == 1 && R == 1 && C == 1) // Robot perfectly aligned at junction
    {
        rlink.command(rlink.command(MOTOR_2_GO, 0.35*SPEED); // L Motor Forward
        rlink.command(rlink.command(MOTOR_1_GO, 0.35*SPEED + 128); // R Motor Backward
        delay (1000); // Ensure robot has pivoted off starting junction
        
        while(true)
        {
            R, L, C = rlink.request('Binary IR Sensor Data');
            
            if(C == 1, R == 1, L == 1)
            {
                rlink.command(rlink.command(MOTOR_2_GO, 0); // L Motor Stop
                rlink.command(rlink.command(MOTOR_1_GO, 0); // R Motor Stop
                turn_complete = 1;
                break;
            }
        }
    }
    else if (C == 1 and L == 0 and R == 0 ) // Junction overshot
    {
        
        rlink.command(rlink.command(MOTOR_2_GO, 0.1*SPEED + 128); // L Motor Reverse
        rlink.command(rlink.command(MOTOR_1_GO, 0.1*SPEED + 128); // R Motor Reverse

        while(true)
        {
            R, L, C = rlink.request('Binary IR Sensor Data');
            
            if(C == 1, R == 1, L == 1)
            {
                rlink.command(rlink.command(MOTOR_2_GO, 0); // L Motor Stop
                rlink.command(rlink.command(MOTOR_1_GO, 0); // R Motor Stop
                break;
            }
        }
                              
        right_turn();
    }
                              
    if(turn_complete == 1 and (C != 1 or R != 1 or L != 1)) // Check turn completed properly
    {
        
    }
}

void left_turn()
{
    R, L, C = rlink.request('Binary IR Sensor Data');
    
    if(L == 1 && R == 1 && C == 1) // Robot perfectly aligned at junction
    {
        rlink.command(rlink.command(MOTOR_1_GO, 0.35*SPEED); // R Motor Forward
        rlink.command(rlink.command(MOTOR_2_GO, 0.35*SPEED + 128); // L Motor Backward
        delay (1000); // Ensure robot has pivoted off starting junction
        
        while(true)
        {
            R, L, C = rlink.request('Binary IR Sensor Data');
            
            if(C == 1, R == 1, L == 1)
            {
                rlink.command(rlink.command(MOTOR_2_GO, 0); // L Motor Stop
                rlink.command(rlink.command(MOTOR_1_GO, 0); // R Motor Stop

                break;
            }
        }
                              
        
    }
    else if (C == 1 and L == 0 and R == 0 ) // Junction overshot
    {
        
        rlink.command(rlink.command(MOTOR_2_GO, 0.1*SPEED + 128); // L Motor Reverse
        rlink.command(rlink.command(MOTOR_1_GO, 0.1*SPEED + 128); // R Motor Reverse

        while(true)
        {
            R, L, C = rlink.request('Binary IR Sensor Data');
            
            if(C == 1, R == 1, L == 1)
            {
                rlink.command(rlink.command(MOTOR_2_GO, 0); // L Motor Stop
                rlink.command(rlink.command(MOTOR_1_GO, 0); // R Motor Stop
                break;
            }
        }
                              
        left_turn();
    }
}

                          
                          

