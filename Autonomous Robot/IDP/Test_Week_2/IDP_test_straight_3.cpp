/
//  IDP_main.cpp
//  
//
//  Created by Admin on 11/10/17.
//
//


#include <stdio.h>
#include <stopwatch.h>
#include <delay.h>
#include <iostream>
using namespace std;
#include <robot_instr.h>
#include <robot_link.h>
#include "IDP_test.h"

robot_link  rlink; // datatype for the robot link
int junction_counter = 0;
int critical_junction = 1;
int IR; /**
         * To record sensor data (should buffer be used so that history
         * of sensor data can be leveraged?
         */

int crit = 0; // To signify when critical junction reached
int sens = 1; // For futher development if speeds need to be refined in subsequent loops
stopwatch sw; // To be used to measure time in junction_checker

int main()
{
    if (!rlink.initialise (ROBOT_NUM)) // setup the link
	{      
		
		cout << "Cannot initialise link" << endl;
		rlink.print_errs("    ");
		return -1;
	}
    
    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // Start Sequence: Moving off a junction
    rlink.command(MOTOR_2_GO, 0.7*SPEED);
    
    IR = rlink.request(READ_PORT_7);
    
    while(IR == CRL or IR == RL)
    {
		cout << "moving off junction" << endl;
        IR = rlink.request(READ_PORT_7);
    } // End sequence
    
    while(true)
    {
        IR = rlink.request(READ_PORT_7);
        
        if(IR == L or IR == CL) // Veering Right
        {
			while (IR == L or IR == CL)
			{
                IR = rlink.request(READ_PORT_7);
				rlink.command(MOTOR_1_GO, sens*0.5*SPEED +128); // L Motor Ease Off
                crit = junction_checker(500);
				if (crit == 1) 
				{
					break;
				}
				rlink.command(MOTOR_2_GO, sens*0.6*SPEED); // R Motor Slow for Correction
				rlink.command(MOTOR_1_GO, sens*0.7*SPEED +128); // L Motor Normal
                crit = junction_checker(500);
				if (crit == 1) 
				{
					break;
				}
			}
		}
        
        if(IR == R or IR == CR) // Veering Left
        {
            while (IR == R or IR == CR)
            {
                IR = rlink.request(READ_PORT_7);
                rlink.command(MOTOR_2_GO, sens*0.5*SPEED); // R Motor Ease Off
                crit = junction_checker(500);
                if (crit == 1)
                {
                    break;
                }
                rlink.command(MOTOR_1_GO, sens*0.6*SPEED + 128); // L Motor Slow for Correction
                rlink.command(MOTOR_2_GO, sens*0.7*SPEED); // R Motor Normal
                crit = junction_checker(500);
                if (crit == 1) 
                {
                    break;
                }
            }
        }
        
        if( IR == NONE) // if line lost
        {
            rlink.command(MOTOR_2_GO, 0); // R Motor Stop
            rlink.command(MOTOR_1_GO, 0); // L Motor Stop
            delay(300);
            rlink.command(MOTOR_2_GO, 0.3*SPEED); // R Reverse
            rlink.command(MOTOR_1_GO, 0.3*SPEED); // L Reverse
            while(IR == NONE)
            {
                IR = rlink.request(READ_PORT_7);
            }
            rlink.command(MOTOR_2_GO, 0); // R Motor Stop
            rlink.command(MOTOR_1_GO, 0); // L Motor Stop
            cout << "Last Reading: " << IR << endl;
            break;
        }
        /**
         * Next step will be to manouver robot based on what sensor 
         * sensor reading comes up. Also incorporate junction_checker
         * to subtract junction counts. Should robot find junction to 
         * align itself?
         */
    }
    
    return 0;
}

void junction_checker(int time)
{
	int crit = 0;
    sw.start();
	while(sw.read() < time)
	{
		IR = rlink.request(READ_PORT_7);
		if (IR == CRL or IR == RL)
		{
			junction_counter = junction_counter + correct;
			cout << "junction counted during veering R" << endl;
			if(junction_counter == critical_junction)
			{
				rlink.command(MOTOR_2_GO, 0); // R Motor Stop
				rlink.command(MOTOR_1_GO, 0); // L Motor Stop
				cout << "reached crit junction after veering R" << endl;
				critc = 1;
				break;
			}
			else
			{
				while(IR == CRL or IR == RL) //move off junction
				{
					IR = rlink.request(READ_PORT_7);
					rlink.command(MOTOR_2_GO, 0.6*SPEED); // R Motor Stop
					rlink.command(MOTOR_1_GO, 0.6*SPEED+128); // L Motor Stop
					cout << "moving off junction" << endl;
				}
				break;
			}
		}
	}
    sw.stop();
	
	return crit;
}


        
