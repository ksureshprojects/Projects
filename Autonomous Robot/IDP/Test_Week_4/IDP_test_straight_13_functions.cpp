
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
#include "IDP_test_13.h"


void junction_checker(); //put in header
void straight_path(); //put in header

int ballcount;
int orientation;
int balls_array[6];
int last_action;
int dropcount;
int lastball;


void junction_checker()
{
	IR = rlink.request(READ_PORT_7);
	if ((IR | 248) == CRL or (IR | 248) == RL)
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
            delay(1000); // pause for peace
		}
		else
		{
			while((IR | 248) == CRL or (IR | 248) == RL) //move off junction
			{
				IR = rlink.request(READ_PORT_7);
				cout << "moving off junction" << endl;
			}
		}
	}
}

void straight_path()
{
	rlink.command (RAMP_TIME, 40); // Set ramp to stop at junction square
    rlink.command(MOTOR_1_GO, SPEED + 128); // Start Sequence: Moving off a junction
    rlink.command(MOTOR_2_GO, SPEED);
    
    stopwatch straight_sw; // Count time to move off junction
    
    IR = rlink.request(READ_PORT_7);
    cout << (IR | 248) << endl;
    
    straight_sw.start();
    while(straight_sw.read() < 1000) // Moving off start junction
    {
        cout << "moving off junction" << endl;
    } 
    straight_sw.stop();
    
    while(true)
    {
        IR = rlink.request(READ_PORT_7);
        cout << (IR | 248)  << endl;
        
        if((IR | 248) == CL) // Veering Right
        {
			last_action = 1; // Record last action
            rlink.command(MOTOR_1_GO, 0.9*SPEED + 128); // L Motor Ease off
            while ((IR | 248) == CL)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer Right " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == CR) // Veering Left
        {
			last_action = 2; // Record last action
            rlink.command(MOTOR_2_GO, 0.9*SPEED); // R Motor Ease off
            while ((IR | 248) == CR)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer Left " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED + 128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
		if((IR | 248) == L) // Large veer Right
        {
			last_action = 3; // Record last action
            rlink.command(MOTOR_2_GO, 0.8*SPEED); // L Motor Really Ease off
            rlink.command(MOTOR_1_GO, 0.7*SPEED + 128); // R also eases off
            while ((IR | 248) == L)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer right Big " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == R) // Large veer Left
        {
			last_action = 4; // Record last action
            rlink.command(MOTOR_2_GO, 0.7*SPEED); // L Motor also Ease off
            rlink.command(MOTOR_1_GO, 0.8*SPEED + 128); // R Really eases off
            while ((IR | 248) == R)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto end;
                }
                cout << "Veer left Big " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        junction_checker(); // Exit if crit junc reached
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
    cout << "Turning Left"  << endl;
    
    stopwatch lturn;
    
	rlink.command (RAMP_TIME, 0); // To make stopping abrupt
    rlink.command(MOTOR_2_GO, 0.8*80); // L Motor forward
    rlink.command(MOTOR_1_GO, 0.8*80); // R Motor reverse
    delay(2600); // Small delay to correct for any initial changes in back sensor output
	
	lturn.start();
    while(true)
    {
		IR = rlink.request(READ_PORT_7);
		cout << IR  << endl;
		if(((IR & 8) == 8) or lturn.read() > 2750) // see if back sensor on line or time exceeded
		{
			cout << "Breaking"  << endl;
			rlink.command(MOTOR_2_GO, 0); // L Motor stop
			rlink.command(MOTOR_1_GO, 0); // R Motor stop
			break;
		}
    }
    lturn.stop();
    delay(500); // pause for peace
}

void right_turn()
{ 
    cout << "Turning Right"  << endl;
    
    stopwatch rturn;
    
	rlink.command (RAMP_TIME, 0); // To make stopping abrupt
    rlink.command(MOTOR_2_GO, 0.8*80 + 128); // L Motor forward
    rlink.command(MOTOR_1_GO, 0.8*80 + 128); // R Motor reverse
    delay(2600); // Small delay to correct for any initial changes in back sensor output
	
	rturn.start();
    while(true)
    {
		IR = rlink.request(READ_PORT_7);
		cout << IR  << endl;
		if(((IR & 8) == 8) or rturn.read() > 2750) // see if back sensor on line or time exceeded
		{
			cout << "Breaking"  << endl;
			rlink.command(MOTOR_2_GO, 0); // L Motor stop
			rlink.command(MOTOR_1_GO, 0); // R Motor stop
			break;
		}
    }
    rturn.stop();
    delay(500); // pause for peace
}

void u_turn()
{ 
    cout << "U TURN"  << endl;
	rlink.command (RAMP_TIME, 0);
    rlink.command(MOTOR_2_GO, 0.8*80 + 128); // L Motor forward
    rlink.command(MOTOR_1_GO, 0.8*80 + 128); // R Motor reverse
    delay(5000); // Small delay to correct for any initial changes in back sensor output
	
    while(true)
    {
		IR = rlink.request(READ_PORT_7);
		cout << IR  << endl;
		if((IR & 8) == 8) // // see if back sensor on line
		{
			cout << "Breaking"  << endl;
			rlink.command(MOTOR_2_GO, 0); // L Motor stop
			rlink.command(MOTOR_1_GO, 0); // R Motor stop
			break;
		}
    }
    rlink.command (RAMP_TIME, 40); //set back to normal for rest of function
    delay(500); // pause for peace
}

void pick_up()
{
	//int buff;
	
	rlink.command (RAMP_TIME, 0);   
    
    rlink.command(MOTOR_4_GO, SWEEPSPEED + 128); // start sweeping
	delay(500);
	rlink.command(MOTOR_4_GO, SWEEPSPEED ); // return sweepers
	delay(500);
	rlink.command(MOTOR_4_GO, 0); // Stop sweepers
	// delay(1000);
	
	
	balls_array[ballcount] = ball_type(); //Store type of ball
	cout << balls_array[ballcount] << endl;
	//cin >> buff;
	
	led_value(balls_array[ballcount]); // Light Ball LED
	//cin >> buff;
	
	ballcount++; // increment ball count
	rlink.command(WRITE_PORT_0, 64);// Retract top actuator
	delay(1500);
	// Extend actuator moved
	//cin >> buff;
	
	critical_junction = 1; // Reverse until previous junction
    IR = rlink.request(READ_PORT_7);
    rlink.command(MOTOR_1_GO, 0.6*80); // Reverse slowly
	rlink.command(MOTOR_2_GO, 0.6*80 + 128);
	delay(1000);
    
    rlink.command(WRITE_PORT_0, 0); // Extend top actuator
    
    while(true)
    {
        junction_checker();
		if (crit == 1)
		{
			crit = 0;
			break;
		}
    }
    
}

void led_value(int balltype)
{
	int read;
	int write = 0;
	
	read = 15 & rlink.request(READ_PORT_7);
	rlink.command(WRITE_PORT_7, read + 112);
	read = read + 112;
	
	if (balltype == 1 or balltype == 2)
	{	
		write = read - 16;
		cout << "Writing" << write << endl;
	}
	else if (balltype == 3 or balltype == 4)
	{
		write = read - 32;
		cout << "Writing" << write << endl;
	}
	else if (balltype == 5)
	{
		write = read - 48;
		cout << "Writing" << write << endl;
	}
	else if (balltype == 6)
	{
		write = read;
		cout << "Writing" << write << endl;
	}
	
	
	rlink.command(WRITE_PORT_7, write);
	delay(1500);
	rlink.command(WRITE_PORT_7, 255);
}

int ball_type()
{
	/*
	if(weightswitch == 64) //ball heavy
	{
		if (154 <= ldr)
		{
			return YELH;
		}
		else
		{
			return WHIH;
		}  
	}
	else
	{
		if (151 < ldr )
		{
			return WHIL; //142-145 multi
		}
		else if (146 < ldr)
		{
			return YELL; //153 - 151
		}
		else
		{
			return MULT;  //146-149
		}
        // MISS type
	}*/
    
    int ldr_count = 0;
    int weightswitch;
    
    stopwatch pick_sw;
    
    //cin >> buff
	
    pick_sw.start();
    while(ldr_count < 250 and pick_sw.read() < 4000)
    {
        weightswitch = 64 & rlink.request(READ_PORT_7);
        ldr += rlink.request(ADC0);
        ldr_count++;
        
    }
    pick_sw.stop();
    
    ldr = ldr/ldr_count;
    
	if(weightswitch == 64) //ball heavy
	{
		if ( 136 < ldr)
		{
			return YELH;
		}
		else
		{
			return WHIH;
		}  
	}
	else
	{
		if(137 < ldr)
		{
			return MISS;
		}
		else if (135 <= ldr )
		{
			return WHIL;
		}
        else if (134 == ldr)
        {
            return ball_type();
        }
		else if (133 == ldr)
		{
			return YELL;
		}
		else
		{
			return MULT;  //146-149
		}
        // MISS type
	}
	
}

void drop_off()
{
	rlink.command (RAMP_TIME, 40);
    stopwatch drop_sw;

    int dropdel; //Time for robot to move until bin
    
    
    if(final_array[dropcount] % 2 == 0) //if heavy ball
    {
        dropdel = 1400; // CHECK THIS
    }
    else // light ball
    {
        dropdel = 5200;
    }
    
    rlink.command(MOTOR_1_GO, 0.9*SPEED +128); // Start Sequence: Moving off a junction
    rlink.command(MOTOR_2_GO, 0.9*SPEED);
    
    drop_sw.start();
    
    while(drop_sw.read() < dropdel)
    {
        IR = rlink.request(READ_PORT_7);
        cout << IR << endl;
        
        if((IR | 248) == CL) // Veering Right
        {
			last_action = 1; // Record last action
            rlink.command(MOTOR_1_GO, 0.8*SPEED + 128); // L Motor Ease off
            while ((IR | 248) == CL)
            {
                IR = rlink.request(READ_PORT_7);
                cout << "Veer Right " << IR << endl;
                if (drop_sw.read() > 5200)
				{
					cout << "Veer Exit " << IR << endl;
					goto end_drop;
				}
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == CR) // Veering Left
        {
			last_action = 2; // Record last action
            rlink.command(MOTOR_2_GO, 0.8*SPEED); // R Motor Ease off
            while ((IR | 248) == CR)
            {
                IR = rlink.request(READ_PORT_7);
                cout << "Veer Left " << IR << endl;
                if (drop_sw.read() > 5200)
				{
					cout << "Veer Exit " << IR << endl;
					goto end_drop;
				}
            }
            rlink.command(MOTOR_1_GO, SPEED + 128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == L) // Large veer Right
        {
			last_action = 3; // Record last action
            rlink.command(MOTOR_1_GO, 0.7*SPEED+128); // L Motor Really Ease off
            rlink.command(MOTOR_1_GO, 0.8*SPEED + 128); // R also eases off
            while ((IR | 248) == L)
            {
                IR = rlink.request(READ_PORT_7);
                cout << "Veer right Big " << IR << endl;
                if (drop_sw.read() > 5200)
				{
					cout << "Veer Exit " << IR << endl;
					goto end_drop;
				}
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == R) // Large veer Left
        {
			last_action = 4; // Record last action
            rlink.command(MOTOR_2_GO, 0.8*SPEED); // L Motor also Ease off
            rlink.command(MOTOR_2_GO, 0.7*SPEED); // R Really eases off
            while ((IR | 248) == R)
            {
                IR = rlink.request(READ_PORT_7);
                cout << "Veer left Big " << IR << endl;
                if (drop_sw.read() > 5200)
				{
					cout << "Veer Exit " << IR << endl;
					goto end_drop;
				}
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Slow Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        } 
    }
    drop_sw.stop();
    
end_drop:
    
    rlink.command(MOTOR_1_GO, 0); // Stop
    rlink.command(MOTOR_2_GO, 0);
    
    //drop ball, activate actuator
    
    
    
    do // Check if subsequent balls the same
    {
        delay(1000);
		rlink.command(WRITE_PORT_0, 128);
		delay(2500);
		rlink.command(WRITE_PORT_0, 0);
		delay(500);
		rlink.command(WRITE_PORT_0, 128);
		delay(750);
		rlink.command(WRITE_PORT_0, 0);
        dropcount ++;
        
        if(dropcount > lastball)
        {
            break;
        }
    }
    while (final_array[dropcount - 1] == final_array[dropcount]);
        
   
    
    rlink.command(MOTOR_1_GO, 0.9*SPEED); // Reverse
    rlink.command(MOTOR_2_GO, 0.9*SPEED + 128);
    delay(1500);
    rlink.command(MOTOR_1_GO, 0); // Stop
    rlink.command(MOTOR_2_GO, 0);
    delay(500);
    u_turn(); //u turn!!!
    
    rlink.command(MOTOR_1_GO, 0.6*SPEED +128); // Start
    rlink.command(MOTOR_2_GO, 0.6*SPEED);
    
    critical_junction = 1;
    IR = rlink.request(READ_PORT_7);
    
    while(true)
    {
        IR = rlink.request(READ_PORT_7);
        cout << IR << endl;
        
        if((IR | 248) == CL) // Veering Right
        {
			last_action = 1; // Record last action
            rlink.command(MOTOR_1_GO, 0.9*SPEED + 128); // L Motor Ease off
            while ((IR | 248) == CL)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto dropped;
                }
                cout << "Veer Right " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED +128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == CR) // Veering Left
        {
			last_action = 2; // Record last action
            rlink.command(MOTOR_2_GO, 0.9*SPEED); // R Motor Ease off
            while ((IR | 248) == CR)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto dropped;
                }
                cout << "Veer Left " << IR << endl;
            }
            rlink.command(MOTOR_1_GO, SPEED + 128); // Back to normal
            rlink.command(MOTOR_2_GO, SPEED);
        }
        
		if((IR | 248) == L) // Large veer Right
        {
			last_action = 3; // Record last action
            rlink.command(MOTOR_2_GO, 0.8*SPEED); // L Motor also Ease off
            rlink.command(MOTOR_1_GO, 0.7*SPEED + 128); // R Really eases off
            while ((IR | 248) == L)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto dropped;
                }
                cout << "Veer right Big " << IR << endl;
            }
            //rlink.command(MOTOR_1_GO, SPEED +128); // Slow Back to normal
            //rlink.command(MOTOR_2_GO, SPEED);
        }
        
        if((IR | 248) == R) // Large veer Left
        {
			last_action = 4; // Record last action
            rlink.command(MOTOR_2_GO, 0.7*SPEED); // L Motor also Ease off
            rlink.command(MOTOR_1_GO, 0.8*SPEED + 128); // R Really eases off
            while ((IR | 248) == R)
            {
                junction_checker();
                if (crit == 1) // Exit if crit junc reached
                {
					crit = 0;
                    goto dropped;
                }
                cout << "Veer left Big " << IR << endl;
            }
            //rlink.command(MOTOR_1_GO, SPEED +128); // Slow Back to normal
            //rlink.command(MOTOR_2_GO, SPEED);
        }
        
        junction_checker(); // Exit if crit junc reached
        if (crit == 1) 
        {
			crit = 0;
            goto dropped;
        } 
    }
dropped:
    cout << "Done Drop" << endl;
    rlink.command (RAMP_TIME, 80);
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
    lastball = 0;
    
    for (int c = 0; c < 4; c++) //check ball array for misses
    {
        if (balls_array[c] != MISS)
        {
            final_array[lastball] = balls_array[c];
            if(c == 3)
            {
                break;
            }
            lastball++;
        }
    }
    
    for (int i = 0; i <= lastball; i++)
    {
		cout << "ball " << i << endl;
        
        if(i < lastball) //one drop off for same balls in series
        {
            while(final_array[i] == final_array[i+1])
            {
                i++;
                if (i == lastball)
                {
                    break;
                }
            }
        }
		
        if (final_array[i] % 2 == 0)  // Find Node corresponding to ball
        {
			cout << "Heavy ball type " << endl;
            next_node = NODR;
        }
        else
        {
			cout << "Light ball type " << final_array[i] << endl;
            next_node = ((final_array[i] - 5)/(-2)) + 1;
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
		cout << "Path interpret " << i << endl;
		critical_junction = path [i][0]; // Set the critical junction counter based on the path input
		
		if (critical_junction != 0)
		{
			cout << "Straight path, CJ " << critical_junction << endl;
			straight_path(); // Go forward untill you reach the critical junction
		}
		
		action = path[i][1];
		
		switch(action)
		{
			case LEFT : cout << "Action " << action << endl;
						left_turn();
						break;
			case RIGHT :cout << "Action " << action << endl; 
						right_turn();
						break;
			case DROP : cout << "Action " << action << endl;
						drop_off();
						break;
			case PICK : cout << "Action " << action << endl;
						pick_up();
						break;
			default : 	cout << "Path can't be interpreted" << endl;
						break;
		}
	}

}
