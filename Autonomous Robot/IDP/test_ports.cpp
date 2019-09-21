#include <iostream>
using namespace std;
#include <robot_instr.h>
#include <robot_link.h>
#include <stopwatch.h>
#define ROBOT_NUM  3                         // The id number (see below)
robot_link  rlink;                            // datatype for the robot link


int main ()
{
	
	if (!rlink.initialise (ROBOT_NUM)) // setup the link
	{      
		
		cout << "Cannot initialise link" << endl;
		rlink.print_errs("    ");
		return -1;
	}
	
	int speed = 100;
	
	
	rlink.command(MOTOR_1_GO, speed);
	rlink.command(MOTOR_2_GO, speed);
	/*
	while(true)
	{
		v = rlink.request(READ_PORT_7)
	}
	*/
	
	//rlink.command(BOTH_MOTORS_GO_SAME, speed);
	//rlink.command(MOTOR_3_GO, speed);
	//rlink.command(MOTOR_4_GO, speed);
	
	int swi = 1;
	while(swi != 0)
	{
		cin >> swi;
	}
	cout << "Speed In " << speed << endl;
	//speed = rlink.request(MOTOR_1);
	//cout << "Speed Out " << speed << endl;
	//blue connector not working
	
	

}
