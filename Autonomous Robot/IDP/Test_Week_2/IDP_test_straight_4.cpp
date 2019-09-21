
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

// extern in header
robot_link  rlink; // datatype for the robot link
int junction_counter = 0;
int critical_junction = 2;
int IR; // To record sensor data
int IR1; // To record last change in reading
int crit = 0; // To signify when critical junction reached

void junction_checker();
void straight_path();

int main()
{
    if (!rlink.initialise (ROBOT_NUM)) // setup the link
	{      
		
		cout << "Cannot initialise link" << endl;
		rlink.print_errs("    ");
		return -1;
	}
    
    straight_path();
    delay(1000);
    right_turn();
    delay(1000);
    left_turn();

}

