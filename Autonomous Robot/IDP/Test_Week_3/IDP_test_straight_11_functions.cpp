
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
#include "IDP_test_10.h"


void junction_checker(); //put in header
void straight_path(); //put in header

int ballcount;
int orientation;
int balls_array[6];

void junction_checker()
{
	IR = rlink.request(READ_PORT_7);
	if (IR|248 == CRL or IR|248 == RL)
	{
		junction_counter ++;
		cout << "junction counted during veering" << endl;
		if(junction_counter == critical_junction)
		{
			rlink.command(MOTOR_2_GO, 0); // R Motor Stop
			rlink.command(MOTOR_1_GO, 0); // L Motor Stop
			cout << "reached crit junction after veering" << endl;
			junction_counter = 0;
			crit = 1;
            delay(1500); // pause for peace
		}
		else
		{
			while(IR|248 == CRL or IR|248 == RL) //move off junction
			{
				IR = rlink.request(READ_PORT_7);
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
    
    while(IR|248 == CRL or IR|248 == RL)
    {
        cout << "moving off junction" << endl;
        IR = rlink.request(READ_PORT_7);
    } // End sequence
    
    while(true)
    {
        IR = rlink.request(READ_PORT_7);
        cout << IR << endl;
        
        if(IR|248 == CL) // Veering Right
        {
            rlink.command(MOTOR_1_GO, 0.85*SPEED + 128); // L Motor Ease off
            while (IR|248 == CL and IR&9 != 9)
            {
                junction_checker();
                if (crit == 1)
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer Right " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if(IR|248 == CR) // Veering Left
        {
            rlink.command(MOTOR_2_GO, 0.85*SPEED); // R Motor Ease off
            while (IR|248 == CR and IR&9 != 9)
            {
                junction_checker();
                if (crit == 1)
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer Left " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED + 128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
		if(IR|248 == L) // Large veer Right
        {
            rlink.command(MOTOR_1_GO, 0.75*SPEED+128); // L Motor Really Ease off
            //rlink.command(MOTOR_1_GO, 0.7*SPEED + 128); // R also eases off
            while (IR|248 == L and IR&9 != 9)
            {
                junction_checker();
                if (crit == 1)
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer right Big " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, 0.95*SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, 0.95*SPEED);
        }
        
        if(IR|248 == R) // Large veer Left
        {
            //rlink.command(MOTOR_2_GO, 0.7*SPEED); // L Motor also Ease off
            rlink.command(MOTOR_2_GO, 0.75*SPEED); // R Really eases off
            while (IR|248 == R and IR&9 != 9)
            {
                junction_checker();
                if (crit == 1)
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer left Big " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, 0.95*SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, 0.95*SPEED);
        } 
        
        junction_checker();
        if (crit == 1) 
        {
			crit = 0;
            goto end;
        } 
    }
	end:
	cout << "Done Straight Path" << endl;
}

void left_turn()
{
    cout << "Turning Right"  << endl;
    
    rlink.command(MOTOR_1_GO, 0.9*SPEED); // L Motor Reverse
    rlink.command(MOTOR_2_GO, 0.9*SPEED); // R Motor Forward
    delay(1000); // Small delay to correct for any initial changes in back sensor output

    while(true)
    {
		IR = rlink.request(READ_PORT_7);
		cout << IR  << endl;
		if(IR&8 == 8) // 8 is all the IR states with back sensor detecting the line
		{
			cout << "Breaking"  << endl;
			rlink.command(MOTOR_2_GO, 0); // L Motor forward
			rlink.command(MOTOR_1_GO, 0); // R Motor reverse
			break;
		}
	}
    delay(1500); // pause for peace
}


void right_turn()
{ 
    cout << "Turning Right"  << endl;

    rlink.command(MOTOR_2_GO, 0.9*SPEED + 128); // L Motor forward
    rlink.command(MOTOR_1_GO, 0.9*SPEED + 128); // R Motor reverse
    delay(1000); // Small delay to correct for any initial changes in back sensor output
  
    while(true)
    {
		IR = rlink.request(READ_PORT_7);
		cout << IR  << endl;
		if(IR&8 == 8) // 32 is all the IR states with back sensor detecting the line
		{
			cout << "Breaking"  << endl;
			rlink.command(MOTOR_2_GO, 0); // L Motor stop
			rlink.command(MOTOR_1_GO, 0); // R Motor stop
			break;
		}
    }
    delay(1500); // pause for peace
    
}

int ball_type(int weightswitch, int colour)
{
	return 0;
}

void pick_up()
{
	// int weightswitch;
	// int color;
	// globally declared ballcount and ball array
	// rlink.command(MOTOR_3_GO, SWEEPSPEED); // start sweeping
	// delay(x);
	// rlink.command(MOTOR_3_GO, SWEEPSPEED + 128); // return sweepers
	// delay(x);
	
	// weightswitch = rlink.request(READ_PORT_7/0);
	// color = rlink.request(ADC);
	
	// balls_array[ballcount] = ball_type(weightswitch, color);
	// ballcount++;
	
	// rlink.command(WRITE_PORT_7, ball);
	// delay(x)
	// rlink.command(WRITE_PORT_7, DEFAULT);
	delay(2000);
	stopwatch sw;
	rlink.command(MOTOR_1_GO, 0.6*SPEED); // Reverse slowly
    rlink.command(MOTOR_2_GO, 0.6*SPEED + 128);
    delay(500); //move off drop junction;
    IR = 248 | rlink.request(READ_PORT_7);
    sw.start();
	while (IR != CRL and sw.read() < 2000)
	{
		IR = 248 | rlink.request(READ_PORT_7);
	}
    sw.stop();
	
	rlink.command(MOTOR_1_GO, 0); // Stop
    rlink.command(MOTOR_2_GO, 0);
    if (ballcount < 6)
    {
		left_turn();
	}
	else
	{
		right_turn();
	}
    
}


void drop_off()
{
    stopwatch sw;

    rlink.command(MOTOR_1_GO, 0.9*SPEED +128); // Start Sequence: Moving off a junction
    rlink.command(MOTOR_2_GO, 0.9*SPEED);
    
    sw.start();
    
    IR = rlink.request(READ_PORT_7);
    
    while(IR|248 == CRL or IR|248 == RL)
    {
        cout << "moving off junction" << endl;
        IR = rlink.request(READ_PORT_7);
    } // End sequence
    
    while(sw.read() < 4000)
    {
        IR = rlink.request(READ_PORT_7);
        cout << IR << endl;
        
        if(IR|248 == CL) // Veering Right
        {
            rlink.command(MOTOR_1_GO, 0.8*SPEED + 128); // L Motor Ease off
            while (IR|248 == CL and IR&9 != 9)
            {
                IR = rlink.request(READ_PORT_7);
                cout << "Veer Right " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if(IR|248 == CR) // Veering Left
        {
            rlink.command(MOTOR_2_GO, 0.8*SPEED); // R Motor Ease off
            while (IR|248 == CR and IR&9 != 9)
            {
                IR = rlink.request(READ_PORT_7);
                cout << "Veer Left " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED + 128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
    }
    sw.stop();
    
    rlink.command(MOTOR_1_GO, 0); // Stop
    rlink.command(MOTOR_2_GO, 0);
    
    //drop ball, activate actuator
    delay(2000);
    
    rlink.command(MOTOR_1_GO, 0.9*SPEED); // Reverse
    rlink.command(MOTOR_2_GO, 0.9*SPEED + 128);
    delay(2000);
    rlink.command(MOTOR_1_GO, 0); // Stop
    rlink.command(MOTOR_2_GO, 0);
    delay(1000);
    right_turn(); //u turn!!!
    
    rlink.command(MOTOR_1_GO, 0.9*SPEED +128); // Start
    rlink.command(MOTOR_2_GO, 0.9*SPEED);
    
    critical_junction = 1;
    IR = rlink.request(READ_PORT_7);
    
    while(true)
    {
        if(IR|248 == CL) // Veering Right
        {
            rlink.command(MOTOR_1_GO, 0.85*SPEED + 128); // L Motor Ease off
            while (IR|248 == CL and IR&9 != 9)
            {
                junction_checker();
                if (crit == 1)
                {
                    crit = 0;
                    goto dropped;
                }
                cout << "Veer Right " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if(IR|248 == CR) // Veering Left
        {
            rlink.command(MOTOR_2_GO, 0.85*SPEED); // R Motor Ease off
            while (IR|248 == CR and IR&9 != 9)
            {
                junction_checker();
                if (crit == 1)
                {
                    crit = 0;
                    goto dropped;
                }
                cout << "Veer Left " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED + 128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
    }
dropped:
    cout << "Done Straight Path" << endl;
}


void ori(int change)
{
	orientation = (orientation + change) % 4;
}

vector <vector <int> > path_finder(int balls_array[6])
{
	orientation = 0;
    vector<vector <int> > path;
    vector <int> step1;
    vector <int> step2;
    vector <int> step3;
    vector <int> step4;
    int current_node = 0;
    int next_node;
    int travel_nodes;

    for (int i = 0; i < 6; i++)
    {
		cout << "ball " << i << endl;
		
        if (balls_array[i] % 2 == 0)  // Find Node corresponding to ball
        {
			cout << "Heavy ball type " << endl;
            next_node = NODR;
        }
        else
        {
			cout << "Light ball type " << balls_array[i] << endl;
            next_node = ((balls_array[i] - 5)/(-2)) + 1;
        }
        
        travel_nodes = next_node - current_node;
        cout << "travel nodes " << travel_nodes << endl;
        
        if (travel_nodes < 0) // Travelling South
        {
            if (orientation != SOUTH)
            {
				cout << "South from side junc " << endl;
                step1.push_back(0); step1.push_back(1); ori(-1); // turn left on the spot
                step2.push_back(abs(travel_nodes)); step2.push_back(1); ori(-1); // Travel to next node, turn left
                step3.push_back(0); step3.push_back(3); ori(2); // Drop Ball
                path.push_back(step1); path.push_back(step2); path.push_back(step3); ori(2);  // Assemble Path Stage
                step1.clear(); step2.clear(); step3.clear(); // Clear Steps for next stage
                current_node = next_node; // Update node
                
            }
            else // starting from node DR
            {
				cout << "South from DR" << endl;
                step1.push_back(abs(travel_nodes)); step1.push_back(1); ori(-1); // Travel to next node, turn left
				step2.push_back(0); step2.push_back(3); ori(2); // Drop Ball
				path.push_back(step1); path.push_back(step2); // Assemble Path Stage
                step1.clear(); step2.clear(); // path segment completed
                current_node = next_node; // Update node
            }
        }
        else if (travel_nodes > 0) //Travelling North
        {
			if (orientation != NORTH)
			{
				if(next_node != NODR) 
				{
					cout << "North to side starting from side" << endl;
					step1.push_back(0); step1.push_back(2); ori(1); // turn right on the spot
					step2.push_back(abs(travel_nodes)); step2.push_back(2); ori(1); // Travel to next node, turn right
					step3.push_back(0); step3.push_back(3); ori(2); // Drop Ball
					path.push_back(step1); path.push_back(step2); path.push_back(step3);// Assemble Path Stage
					step1.clear(); step2.clear(); step3.clear(); // Clear Steps for next stage
					current_node = next_node; // Update node
				}
				else // if next node is DR
				{
					cout << "North to DR from side " << endl;
					step1.push_back(0); step1.push_back(2); ori(1); // turn right on the spot
					step2.push_back(abs(travel_nodes)); step2.push_back(3); ori(2); // Travel to next node drop ball
					path.push_back(step1); path.push_back(step2); // Assemble Path Stage
					step1.clear(); step2.clear(); // path segment completed
					current_node = next_node; // Update node
				}
			}
			else // if starting from start node
			{
				if(next_node != NODR)
				{
					cout << "North to side from start " << endl;
					step1.push_back(abs(travel_nodes)); step1.push_back(2); ori(1); // Travel to next node, turn right
					step2.push_back(0); step2.push_back(3); ori(2); // Drop Ball
					path.push_back(step1); path.push_back(step2); // Assemble Path Stage
					step1.clear(); step2.clear();  // Clear Steps for next stage
					current_node = next_node; // Update node
				}
				else // if next node is DR
				{
					cout << "North to DR from Start " << endl;
					step1.push_back(abs(travel_nodes)); step1.push_back(3); ori(2); // travel to node Drop Ball
					path.push_back(step1); // Assemble Path Stage
					step1.clear(); // path segment completed
					current_node = next_node; // Update node
				}
			}
		}
		else // on current node drop ball
		{
			cout << "Same node drop " << endl;
			step1.push_back(0); step1.push_back(2); ori(1); // Uturn
            step2.push_back(0); step2.push_back(2); ori(1); 
			step3.push_back(0); step3.push_back(3); ori(2); // Drop Ball
            path.push_back(step1); path.push_back(step2); path.push_back(step3);// Assemble Path Stage
            step1.clear(); step2.clear(); step3.clear(); // Clear Steps for next stage
            current_node = next_node; // Update node
		}
    }
    
    travel_nodes = abs(0 - current_node); //Calculate nodes to start
    
    if (orientation != SOUTH)
	{ 
		cout << "End from side " << endl;
		step1.push_back(0); step1.push_back(1); // Turn Left
		step2.push_back(abs(travel_nodes)); step2.push_back(1); // Travel to next node, turn left
		step3.push_back(4); step3.push_back(1);  // Travel to start, orient correctly
		// step4.push_back(1); step3.push_back(5); // Travel one junction, END
		path.push_back(step1); path.push_back(step2); path.push_back(step3); // path.push_back(step4);
		step1.clear(); step2.clear(); step3.clear(); //step4.clear(); // path segment completed
		
	}
	else // starting from node DR
	{
		cout << "end from DR " << endl;
		step1.push_back(abs(travel_nodes)); step1.push_back(1); // Travel to next node, turn left
		step2.push_back(4); step2.push_back(1); // Travel to start, orient correctly
		// step3.push_back(1); step3.push_back(5);  // Travel one junction, END
		path.push_back(step1); path.push_back(step2); // path.push_back(step3); 
		step1.clear(); step2.clear(); //step3.clear(); // path segment completed
	}
	
	cout << "returning path" << endl;
	return path;
}


void path_interpret(vector <vector <int> > path)
{
	int action;
	for(int i = 0; i < (int)(path.size()); i++)
	{
		critical_junction = path [i][0]; // Set the critical junction counter based on the path input
		
		if (critical_junction != 0)
		{
			straight_path(); // Go forward untill you reach the critical junction
		}
		
		action = path[i][1];
		
		switch(action)
		{
			case LEFT : left_turn();
						break;
			case RIGHT : right_turn();
						break;
			case DROP : drop_off();
						break;
			case PICK : pick_up();
						break;
			default : cout << "Path can't be interpreted" << endl;
						break;
		}
	}
}
