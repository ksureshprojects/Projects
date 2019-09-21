//
//  IDP_Functions_Test.cpp
//  
//
//  Created by Admin on 12/10/17.
//
//

#include <stdio.h>
#include <stopwatch.h>
#include <delay.h>
#include <iostream>
using namespace std;
#include <robot_instr.h>
#include <robot_link.h>
#include "IDP.h"
//
int orientation;
//extern junction current; // Current junction
//extern junction next; // Junction to travel to next
int IR; //Binary IR sensor data
int junction_counter;
int path_step;

int front_veering(int crit_junc)
{
	cout << "Veering" << endl;
    IR = rlink.request(READ_PORT_7); // Re-Recieve Sensor Data
    stopwatch sw;
    if((IR == L) or (IR == CL)) // Front veering RIGHT
    {
        sw.start();
        while(sw.read() < 3000)
        {
            rlink.command(MOTOR_2_GO, 0.6 * SPEED); // R Motor
            rlink.command(MOTOR_1_GO, 0.4*SPEED + 128); // L Motor
            delay(500);
            rlink.command(MOTOR_2_GO, 0.4 * SPEED); // R Motor
            rlink.command(MOTOR_1_GO, 0.6 *SPEED + 128); // L Motor
            delay(500);
            IR = rlink.request(READ_PORT_7);
                          
            if(IR == C)
            {
                rlink.command(MOTOR_1_GO, 0.7*SPEED +128);
				rlink.command(MOTOR_2_GO, 0.7*SPEED);
                return IR;
            }
            if(IR == CRL)
            {
                junction_counter++;
                cout << "Junction Detected" << junction_counter << endl;
                if(junction_counter == crit_junc)
                {
					rlink.command(MOTOR_2_GO, 0); // R Motor Stop
					rlink.command(MOTOR_1_GO, 0); // L Motor Stop	
					return IR;
				}
                rlink.command(MOTOR_1_GO, 0.7*SPEED +128);
				rlink.command(MOTOR_2_GO, 0.7*SPEED);
                return IR;
            }

        }
        sw.stop();
        
    }
                              
    if((IR == R) or (IR == CR)) // Front veering LEFT
    {
        sw.start();
        while(sw.read() < 3000)
        {
            rlink.command(MOTOR_2_GO, 0.6 * SPEED); // R Motor
            rlink.command(MOTOR_1_GO, 0.4*SPEED + 128); // L Motor
            delay(500);
            rlink.command(MOTOR_2_GO, 0.4 * SPEED); // R Motor
            rlink.command(MOTOR_1_GO, 0.6 *SPEED + 128); // L Motor
            delay(500);
            IR = rlink.request(READ_PORT_7);
                          
            if(IR == C)
            {
                rlink.command(MOTOR_1_GO, 0.7*SPEED +128);
				rlink.command(MOTOR_2_GO, 0.7*SPEED);
                return IR;
            }
            if(IR == CRL)
            {
                junction_counter++;
                cout << "Junction Detected" << junction_counter << endl;
                delay(1500);
                if(junction_counter == crit_junc)
                {
					rlink.command(MOTOR_2_GO, 0); // R Motor Stop
					rlink.command(MOTOR_1_GO, 0); // L Motor Stop	
					return IR;
				}
                rlink.command(MOTOR_1_GO, 0.7*SPEED +128);
				rlink.command(MOTOR_2_GO, 0.7*SPEED);
                return IR;
            }

        }
        sw.stop();
    }
    
    return IR;
    
}

void left_turn()
{
    IR = rlink.request(READ_PORT_7);
    
    // int turn_complete = 0;
    stopwatch sw;
    
    if (IR == C ) // Check if Junction Overshot
    {
        sw.start();
        rlink.command(MOTOR_2_GO, 0.1*SPEED + 128); // R Motor Reverse
        rlink.command(MOTOR_1_GO, 0.1*SPEED); // L Motor Reverse

        while(sw.read() < 3000)
        {
            IR = rlink.request(READ_PORT_7);
            
            if(IR == CRL)
            {
                rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                break;
            }
        }
        sw.stop();
        
    }
    
    if(IR == CRL) // Robot perfectly aligned at junction
    {
        rlink.command(MOTOR_2_GO, 0.35*SPEED + 128); // R Motor Backward
        rlink.command(MOTOR_1_GO, 0.35*SPEED + 128); // L Motor Forward
        delay (1000); // Ensure robot has pivoted off starting junction
        
        while(true)
        {
            IR = rlink.request(READ_PORT_7);
            
            if(IR == CRL)
            {
                rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                break;
            }
        }
    }
                              
    //IR = rlink.request(READ_PORT_7);
                              
    //if(turn_complete == 1 and IR != CRL) // Check turn completed properly
    //{
    //    turn_checking();
    //}
}


void right_turn()
{
    IR = rlink.request(READ_PORT_7);
    stopwatch sw;
    
    if (IR == C ) // Check if Junction Overshot
    {
        sw.start();
        rlink.command(MOTOR_2_GO, 0.1*SPEED + 128); // R Motor Reverse
        rlink.command(MOTOR_1_GO, 0.1*SPEED); // L Motor Reverse

        while(sw.read() < 3000)
        {
            IR = rlink.request(READ_PORT_7);
            
            if(IR == CRL)
            {
                rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                break;
            }
        }
        sw.stop();
        
    }
    
    if(IR == CRL) // Robot perfectly aligned at junction
    {
        rlink.command(MOTOR_2_GO, 0.35*SPEED); // R Motor Forward
        rlink.command(MOTOR_1_GO, 0.35*SPEED); // L Motor Backward
        delay (1000); // Ensure robot has pivoted off starting junction
        
        while(true)
        {
            IR = rlink.request(READ_PORT_7);
            
            if(IR == CRL)
            {
                rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                break;
            }
        }
    }
                              
    //IR = rlink.request(READ_PORT_7);
                              
    //if(turn_complete == 1 and IR != CRL) // Check turn completed properly
    //{
    //    turn_checking();
    //}
}


void execute_action(int action)
{
    switch(action)
    {
        case LEFT : left_turn();
                    break;
        case RIGHT : right_turn();
                     break;
        //case DROP : drop_ball();
                   // break;
        //case PICK : pick_up_ball();
                   // break;
    }
}

void travel(int path[][2])
{
    // To count junctions passed and stage in path.
    junction_counter = 0;
    path_step = 0;
    //try_counter = 0; // For 3rd troubleshooting case
                      
    while(true)
    {
        if ((path[path_step][0] != 0) and junction_counter == 0) //Start robot intially or after action
        {
            rlink.command(MOTOR_1_GO, 0.7*SPEED +128);
			rlink.command(MOTOR_2_GO, 0.7*SPEED);
            delay (750);
        }
                          
        IR = rlink.request(READ_PORT_7);
        cout << "IR " << IR << endl;
        
        if(IR == CR or IR == R or IR == CL or IR == L) // Front veering
        {
			cout << "Could Veer" << endl;
			delay(100);
			
			if (IR != CRL)
			{
				cout << "Veering" << endl;
				IR = front_veering(path[path_step][0]);
			}
        }
        
        //if(IR == RL or IR == NONE or IR == L or IR == R) // Back out of alignment
        //{
        //    IR = back_veering();
        //}
        
        if ((IR == CRL or IR == RL) and path[path_step][0] == 0) // action to be executed on current position
        {
            execute_action(path[path_step][1]); // Call execute action function
            path_step ++; // Move to next stage of path
            if (path_step == (sizeof(path)/(2*sizeof(int))) - 1) // End function if end of path
            {
                break;
            }
        }
        else if (IR == CRL or IR == RL) // Junction passed
        {
            junction_counter++;
            cout << "Junction Detected " << junction_counter << endl;
			if(junction_counter >= path[path_step][0]) // Critical jucntion reached
			{
				cout << "Action Time " << path[path_step][1] << endl;
				junction_counter = 0;
				rlink.command(MOTOR_2_GO, 0); // R Motor Stop
				rlink.command(MOTOR_1_GO, 0); // L Motor Stop
				execute_action(path[path_step][1]); // Call execute action function
				path_step ++;
				if (path_step == (sizeof(path)/(2*sizeof(int))) - 1) // End function if end of path
				{
					break;
				}
			}
			delay(1500);
        }  
    }
}
