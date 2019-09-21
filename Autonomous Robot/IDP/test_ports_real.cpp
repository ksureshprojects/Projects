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
	
	int swi = 1;
	int v, imax;
	imax = 10;
	
	
	for(int i = 0; i < imax; i++)
	{
		cout << "reading1" << endl;
		v = rlink.request (READ_PORT_7);
		cout << "read" << endl;
		cout << v  << endl;
		
		while(true)
		{
			cin >> swi;
			if(swi == 0)
			{
				break;
			}
		}
		
		
	}
	

}
