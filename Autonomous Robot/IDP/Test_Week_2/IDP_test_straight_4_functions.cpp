
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


void junction_checker(); //put in header
void straight_path(); //put in header


void junction_checker()
{
	IR = rlink.request(READ_PORT_7);
	if (IR == CRL /*or IR == RL*/)
	{
		junction_counter ++;
		cout << "junction counted during veering" << endl;
		if(junction_counter == critical_junction)
		{
			rlink.command(MOTOR_2_GO, 0); // R Motor Stop
			rlink.command(MOTOR_1_GO, 0); // L Motor Stop
			cout << "reached crit junction after veering" << endl;
			crit = 1;
		}
		else
		{
			while(IR == CRL or IR == RL) //move off junction
			{
				IR = rlink.request(READ_PORT_7);
				//rlink.command(MOTOR_2_GO, 0.6*SPEED); // R Motor Stop
				//rlink.command(MOTOR_1_GO, 0.6*SPEED+128); // L Motor Stop
				cout << "moving off junction" << endl;
			}
		}
	}
}

void straight_path()
{
    rlink.command(MOTOR_1_GO, SPEED +128); // Start Sequence: Moving off a junction
    rlink.command(MOTOR_2_GO, SPEED);
    
    IR = rlink.request(READ_PORT_7);
    
    while(IR == CRL or IR == RL)
    {
        cout << "moving off junction" << endl;
        IR = rlink.request(READ_PORT_7);
    } // End sequence
    
    while(true)
    {
        IR = rlink.request(READ_PORT_7);
        
        if(IR == CL) // Veering Right
        {
            rlink.command(MOTOR_2_GO, 0.85*SPEED); // L Motor Ease off
            while (IR == CL)
            {
                junction_checker();
                if (crit == 1)
                {
                    goto end;
                }
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if(IR == CR) // Veering Left
        {
            rlink.command(MOTOR_1_GO, 0.85*SPEED + 128); // L Motor Ease off
            while (IR == CL)
            {
                junction_checker();
                if (crit == 1)
                {
                    goto end;
                }
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if(IR == L) // Large veer left
        {
            rlink.command(MOTOR_2_GO, 0.5*SPEED); // L Motor Really Ease off
            rlink.command(MOTOR_1_GO, 0.7*SPEED + 128); // R also eases off
            while (IR == L)
            {
                junction_checker();
                if (crit == 1)
                {
                    goto end;
                }
            }
            rlink.command(MOTOR_1_GO, 0.8*SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, 0.8*SPEED);
        }
        
        if(IR == R) // Large veer Right
        {
            rlink.command(MOTOR_2_GO, 0.7*SPEED); // L Motor also Ease off
            rlink.command(MOTOR_1_GO, 0.5*SPEED + 128); // R Really eases off
            while (IR == R)
            {
                junction_checker();
                if (crit == 1)
                {
                    goto end;
                }
            }
            rlink.command(MOTOR_1_GO, 0.8*SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, 0.8*SPEED);
        }
        
        junction_checker();
        if (crit == 1) 
        {
            goto end;
        }
    }
end:

}

void left_turn()
{
    //position axis on junction
    rlink.command(MOTOR_2_GO, 0.3*SPEED); // L Motor slow
    rlink.command(MOTOR_1_GO, 0.3*SPEED + 128); // R Motor slow
    delay(1000);
    rlink.command(MOTOR_2_GO, 0); // L Motor stop
    rlink.command(MOTOR_1_GO, 0); // R Motor stop
    delay(1000);
    
    //position axis on junction
    rlink.command(MOTOR_2_GO, 0.6*SPEED + 128); // L Motor reverse
    rlink.command(MOTOR_1_GO, 0.6*SPEED + 128); // R Motor forward
    while(IR != CRL)
    {
        IR = = rlink.request(READ_PORT_7);
    }
    rlink.command(MOTOR_2_GO, 0); // L Motor stop
    rlink.command(MOTOR_1_GO, 0); // R Motor stop
}

void right_turn()
{
    //position axis on junction
    rlink.command(MOTOR_2_GO, 0.3*SPEED); // L Motor slow
    rlink.command(MOTOR_1_GO, 0.3*SPEED + 128); // R Motor slow
    delay(1000);
    rlink.command(MOTOR_2_GO, 0); // L Motor stop
    rlink.command(MOTOR_1_GO, 0); // R Motor stop
    delay(1000);
    
    //position axis on junction
    rlink.command(MOTOR_2_GO, 0.6*SPEED); // L Motor forward
    rlink.command(MOTOR_1_GO, 0.6*SPEED); // R Motor reverse
    while(IR != CRL)
    {
        IR = = rlink.request(READ_PORT_7);
    }
    rlink.command(MOTOR_2_GO, 0); // L Motor stop
    rlink.command(MOTOR_1_GO, 0); // R Motor stop
}


        
