#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import argparse
import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui


def get_file_name(path_name):
        """ Gets file name from file path """
        file_name = ""
        for c in path_name[::-1]:
            if c != '/':
                file_name += c
            else:
                break
        file_name = file_name[::-1]
        return file_name


def main(arg_parser):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    # Add check to see if path leads to a .txt file
    if arg_parser.path is not None:
        if arg_parser.path[-3:] != "txt":
            raise TypeError("***ERROR: Please load in a .txt file")
    # Check if user tries to input translation into command line
    # interface
    if arg_parser.c and arg_parser.r:
        print("Cannot launch command line mode with translator")
        sys.exit()
    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(arg_parser.path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    if parser.parse_network():
        if arg_parser.c:
                    # Initialise instance of the userint.UserInterface() class
                    userint = UserInterface(names, devices, network, monitors)
                    userint.command_interface()
        else:
            if arg_parser.r:
                lang = u"el"
            else:
                lang = u"en"
            # Initialise an instance of the gui.Gui() class
            file_name = get_file_name(arg_parser.path)
            title = "Logic Simulator - " + file_name
            app = wx.App()
            gui = Gui(title, arg_parser.path, names, devices, network,
                      monitors, lang)
            gui.Show(True)
            app.MainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-r", action="store_true",
                        help="Option to launch the GUI in Romanian")
    parser.add_argument('-c', action="store_true",
                        help='Option to use command line interface')
    parser.add_argument('--path',
                        default="./test_definition_files/"
                        "circuit_text_files/circuit1.txt",
                        help='OPTIONAL: Relative path to specfile')
    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())
