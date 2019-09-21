//
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
#include "IDP.h"
robot_link  rlink;             // datatype for the robot link

int main()
{
    if (!rlink.initialise (ROBOT_NUM)) // setup the link
	{      
		
		cout << "Cannot initialise link" << endl;
		rlink.print_errs("    ");
		return -1;
	}
    
    int junction_counter = 0;
    int critical_junction = 1;
    int IR;
    stopwatch sw;
    
    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // Start Sequence: Moving off a junction
    rlink.command(MOTOR_2_GO, 0.7*SPEED);
    
    IR = rlink.request(READ_PORT_7);
    
    while(IR == CRL)
    {
        IR = rlink.request(READ_PORT_7);
    } // End sequence
    
    while(true)
    {
        IR = rlink.request(READ_PORT_7);
        
        if(IR == L or IR == CL) // Veering Right
        {
            delay(400); // Check robot not reaching junction
            IR = rlink.request(READ_PORT_7);
            if (IR == L or IR == CL)
            {
                IR = rlink.request(READ_PORT_7);
                sw.start();
                while(IR != C and IR != CRL and sw.read() < 2000)
                {
                    cout << "correcting right veer" << endl;
                    IR = rlink.request(READ_PORT_7);
                    rlink.command(MOTOR_1_GO, 0.5*SPEED +128); // L Motor Ease Off
                    delay(100);
                    rlink.command(MOTOR_2_GO, 0.6*SPEED); // R Motor Slow for Correction
                    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // L Motor Normal
                    delay(100);
                }
                sw.stop();
                
                if (IR == CRL)
                {
                    rlink.command(MOTOR_2_GO, 0.7*SPEED); // R Motor Slow for Correction
                    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // L Motor Normal
                    junction_counter++;
                    cout << "junction counted during veering R" << endl;
                    if(junction_counter == critical_junction)
                    {
                        rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                        rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                        cout << "reached crit junction after veering R" << endl;
                    }
                    else
                    {
                        while(IR == CRL) //move off junction
                        {
                            cout << "moving off junction" << endl;
                            IR = rlink.request(READ_PORT_7);
                        }
                    }
                }
                else if (IR != C)
                {
                    rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                    rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                    cout << "failure to follow R" << endl;
                }
                else
                {
                    rlink.command(MOTOR_2_GO, 0.7*SPEED); // R Motor Slow for Correction
                    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // L Motor Normal
                    cout << "corrected right" << endl;
                }
            }
        }
        
        if(IR == R or IR == CR) // Veering Left
        {
            delay(400); // Check robot not reaching junction
            IR = rlink.request(READ_PORT_7);
            if (IR == R or IR == CR)
            {
                IR = rlink.request(READ_PORT_7);
                sw.start();
                while(IR != C and IR != CRL and sw.read() < 2000)
                {
                    cout << "correcting left veer" << endl;
                    IR = rlink.request(READ_PORT_7);
                    rlink.command(MOTOR_2_GO, 0.5*SPEED +128); // R Motor Ease Off
                    delay(100);
                    rlink.command(MOTOR_1_GO, 0.6*SPEED); // L Motor Slow for Correction
                    rlink.command(MOTOR_2_GO, 0.7*SPEED +128); // R Motor Normal
                    delay(100);
                }
                sw.stop();
                
                if (IR == CRL)
                {
                    rlink.command(MOTOR_2_GO, 0.7*SPEED); // R Motor Slow for Correction
                    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // L Motor Normal
                    junction_counter++;
                    cout << "junction counted during veering L" << endl;
                    if(junction_counter == critical_junction)
                    {
                        rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                        rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                        cout << "reached crit junction after veering L" << endl;
                    }
                    else
                    {
                        while(IR == CRL) //move off junction
                        {
                            cout << "moving off junction" << endl;
                            IR = rlink.request(READ_PORT_7);
                        }
                    }
                }
                else if (IR != C)
                {
                    rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                    rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                    cout << "failure to follow L" << endl;
                    break;
                }
                else
                {
                    rlink.command(MOTOR_2_GO, 0.7*SPEED); // R Motor Slow for Correction
                    rlink.command(MOTOR_1_GO, 0.7*SPEED +128); // L Motor Normal
                    cout << "corrected left L" << endl;
                }
            }
        }
        
        if( IR = NONE) // if line lost
        {
            cout << "line lost" << endl;
            rlink.command(MOTOR_2_GO, 0); // R Motor Stop
            rlink.command(MOTOR_1_GO, 0); // L Motor Stop
            delay(300);
            rlink.command(MOTOR_2_GO, 0.1*SPEED); // Rotate anticlockwise
            rlink.command(MOTOR_1_GO, 0.1*SPEED);
            sw.start()
            while(sw.read()<1000 and IR != C and IR != CR and IR != CL)
            {
                IR = rlink.request(READ_PORT_7);
            }
            sw.stop();
            
            if (IR == C or IR == CR or IR == CL)
            {
                cout << "found line" << endl;
            }
            
            else
            {
                rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                delay(300);
                rlink.command(MOTOR_2_GO, 0.1*SPEED + 128); // Rotate clockwise
                rlink.command(MOTOR_1_GO, 0.1*SPEED + 128);
                sw.start()
                while(sw.read()<1500 and IR != C and IR != CR and IR != CL)
                {
                    IR = rlink.request(READ_PORT_7);
                }
                sw.stop()
                
                if (IR == C or IR == CR or IR == CL)
                {
                    cout << "found line" << endl;
                }
                else
                {
                    cout << "failure to find" << endl;
                    break;
                }
            }
        }
        
        if(IR = CRL) // Junction Found
        {
            junction_counter++
            if(junction_counter == critical_junction)
            {
                rlink.command(MOTOR_2_GO, 0); // R Motor Stop
                rlink.command(MOTOR_1_GO, 0); // L Motor Stop
                cout << "reached crit junction SUCESSSSSSS" << endl;
            }
            else
            {
                while(IR == CRL) //move off junction
                {
                    cout << "moving off junction" << endl;
                    IR = rlink.request(READ_PORT_7);
                }
            }
        }
    }
    
    return 0;
    
    // delivery_path = calculate(); // delivery path
    
    // travel(delivery_path);
}
