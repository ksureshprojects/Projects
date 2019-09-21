//
//  IDP_main.cpp
//  
//
//  Created by Admin on 11/10/17.
//
//

#include <stdio.h>
#include "stopwatch.h"
#include "delay.h"
#include "IDP.h"

int main()
{
    if (!rlink.initialise (ROBOT_NUM)) // setup the link
	{      
		
		cout << "Cannot initialise link" << endl;
		rlink.print_errs("    ");
		return -1;
	}
    
    int path[5][2] = {{4,1},{0,1},{4,1},{4,1},{0,2}};
    
    travel(path);
    
    return 0;
    
    // delivery_path = calculate(); // delivery path
    
    // travel(delivery_path);
}
