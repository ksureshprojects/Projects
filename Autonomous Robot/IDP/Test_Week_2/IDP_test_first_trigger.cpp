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
int IR1;
int IR2;

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
    
    IR1 = rlink.request(READ_PORT_7);
    
    while(IR == CRL or IR == RL)
    {
		cout << "moving off junction" << endl;
        IR = rlink.request(READ_PORT_7);
    } // End sequence
    
    while(true)
    {
        IR1 = rlink.request(READ_PORT_7);
        delay(100);
        IR2  = rlink.request(READ_PORT_7);
        
        if (IR1 != IR2)
        {
            break;
        }
    }
    
    cout << "IR Reading changed from " << IR1 << "to " << IR2 << endl;
    
    return 0;
}

        
