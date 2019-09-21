
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
#include <stdlib.h>
#include <vector>
using namespace std;
#include <robot_instr.h>
#include <robot_link.h>
#include "IDP_test_12.h"

// extern in header
robot_link  rlink; // datatype for the robot link
int junction_counter = 0;
int critical_junction;
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
	rlink.command(WRITE_PORT_0, 0);
   
    int array[17][2] = {{3,2},{1,4},{0,1},{1,2},{1,4},{0,1},{1,2},
					{1,4},{0,1},{1,2},{1,4},{0,1},{1,2},{1,4},{0,2},{7,2},{4,2}}; //{{1,2},{0,4},{0,2},{2,2}}; 
    vector <vector <int> > path;
    vector <int> step;
    rlink.command (RAMP_TIME, 80);
    
    for(int i = 0; i < 17 ; i++)
    {
        for (int j = 0; j < 2; j++)
        {
            step.push_back(array[i][j]);
        }
        
        path.push_back(step); step.clear();
    }
    
    path_interpret(path);
	cout << balls_array[0] << endl;
	cout << balls_array[1] << endl;
	cout << balls_array[2] << endl;
	cout << balls_array[3] << endl;
	cout << balls_array[4] << endl;
	/*int a ,b;
	vector <vector <int> > path;
    vector <int> step;
    
	while(true)
	{
		cin >> a;
		cin >> b;
		
		step.push_back(a);
		step.push_back(b);
		path.push_back(step);
		
		
		path_interpret(path);
		
		path.clear();
		step.clear();
	}*/
	
}

