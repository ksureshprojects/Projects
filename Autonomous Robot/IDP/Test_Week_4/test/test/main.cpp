//
//  main.cpp
//  test
//
//  Created by Admin on 2/11/17.
//  Copyright © 2017 Admin. All rights reserved.
//

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
using namespace std;

#define YELH 4
#define WHIH 2
#define MULT 5
#define WHIL 1
#define YELL 3
#define MISS 6

#define NORTH 0
#define EAST 1
#define SOUTH 2
#define WEST 3

#define LEFT 1
#define RIGHT 2
#define DROP 3
#define PICK 4

#define SPEED 110
#define SWEEPSPEED 120

#define CRL 255
#define C 249
#define CL 251
#define CR 253
#define RL 254
#define NONE 248
#define L 250
#define R 252

#define YELH 4
#define WHIH 2
#define MULT 5
#define WHIL 1
#define YELL 3
#define MISS 6
#define NOD1 3
#define NOD2 2
#define NOD3 1
#define NODR 4

int orientation;
int lastball = 0;
int final_array[6];

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
            lastball++;
            if(c == 3)
            {
                break;
            }
            
        }
    }
    
    for (int i = 0; i < lastball; i++)
    {
        cout << "ball " << i << endl;
        
        if(i < lastball) //one drop off for same balls in series
        {
            while(final_array[i] == final_array[i+1])
            {
                i++;
                if(i == lastball)
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


int main()
{
    int balls_array[6] = {1,2,2,2,2,4};
    lastball = 0;
    
    path_finder(balls_array);
    
    
}
