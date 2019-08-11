import sys
import wx
from names import Names
import builtins
builtins.__dict__['_'] = wx.GetTranslation
"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    Optional Parameters:
        typ: Type of symbol.
        id: Symbol id.
        line_num: Number of line on which symbol occurs.
        line_pos: Position of first character of symbol.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, type_=None, id_=None, pos=None):
        """Initialise symbol properties."""
        self.type = type_
        self.id = id_
        self.pos = pos

    def display(self):
        print("Type: " + str(self.type))
        print("ID: " + str(self.id))
        print("Line Number: " + str(self.line_num))


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    _open_file(self, path, read_only=True): Open and return the file
                                            specified by path.
    _remove_spaces(self): Remove white spaces
    _get_next_symbol(self): Seek the next symbol in self.def_file
    _remove_comment(self, _type): Removes comments from definition file
    get_symbol(self): Translate the next sequence of characters into a symbol
    print_error(self, error_index):Prints the line number, the line containing
                                    the error , and a caret
                                    under the error
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.path = path
        self.broken_comment_msg = ""
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
                                 self.COLON, self.DOT, self.LEFT,
                                 self.RIGHT, self.DASH, self.LOGICTYPE,
                                 self.KEYWORD, self.CONFVAR, self.NAME,
                                 self.EOF] = range(13)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS", "END"]
        self.device_list = ["CLOCK", "SWITCH", "AND",
                            "NAND", "NOR", "OR", "DTYPE", "XOR", "SIGGEN"]
        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,
         self.END_ID] = self.names.lookup(self.keywords_list)

        # Open file
        self.def_file = self._open_file(self.path)
        self.current_character = self.def_file.read(1)
        # Correction if file is empty
        if self.current_character == "":
            self.write_file = self._open_file(self.path, False)
            self.write_file.write(" ")
            self.write_file.close()
            self.def_file.seek(0)
            self.current_character = self.def_file.read(1)

    def _open_file(self, path, read_only=True):
        """Open and return the file specified by path."""
        if read_only:
            try:
                text_file = open(path)
                return text_file
            except IOError:
                print("Error! File could not be opened")
                sys.exit()  # TODO do not sys exit, let user try again
        else:
            try:
                text_file = open(path, 'w')
                return text_file
            except IOError:
                print("Error! File could not be opened")
                sys.exit()  # TODO do not sys exit, let user try again

    def _remove_spaces(self):
        """Remove white spaces"""
        while self.current_character.isspace():
            self.current_character = self.def_file.read(1)

    def _get_next_symbol(self):
        """Seek the next symbol in self.def_file.
        Returns:
            string containing the symbol
            None if EOF
            "$"if unrecognised symbol
         """

        # Remove spaces
        self._remove_spaces()
        name_str = ''
        broken_comment = 0
        # print("Current character:", self.current_character)
        # Remove comment
        while self.current_character in ["#", "/"]:
            if self.current_character == "#":
                broken_comment = self._remove_comment(0)
                self._remove_spaces()
            if self.current_character == "/":
                broken_comment = self._remove_comment(1)
                self._remove_spaces()
        # Check if comment is defined correctly
        if broken_comment:
            self.broken_comment_msg = "***ERROR: Multi line"\
                         "comment not defined correctly"
            print(self.broken_comment_msg)
            return '#'
        # Check if current character is delimiter
        if self.current_character in [":", ";", ",", "=", ".", "(", ")", "-"]:
            # Return current character and retrieve
            # the next character
            current_symbol = self.current_character
            self.current_character = self.def_file.read(1)
            return current_symbol
        elif not self.current_character.isalnum() \
                and self.current_character != '' \
                and not self.current_character == "_":
            self.current_character = self.def_file.read(1)
            return "$"
        elif self.current_character == '':
            return None
        while self.current_character.isalnum()or self.current_character == "_":
            name_str += self.current_character
            self.current_character = self.def_file.read(1)
        return name_str

    def _remove_comment(self, _type):
        """Removes comments from definition file
        _type = 0 if one line comment defined by # and end of line
        _type = 1 if multiple line comment defined by /* ... */

        Returns:
        1 if the comment is defined wrongly
        0 if the comment is defined correctly
        """
        if _type == 0:
            while self.current_character is not '\n':
                self.current_character = self.def_file.read(1)
            self.current_character = self.def_file.read(1)  # Get to next line
            return 0
        elif _type == 1:
            self.current_character = self.def_file.read(1)
            if self.current_character != "*":
                return 1
            self.current_character = self.def_file.read(1)
            while self.current_character == '*':
                self.current_character = self.def_file.read(1)
            print(self.current_character)
            if self.current_character == '':
                return 1
            if self.current_character == "/":
                self.current_character = self.def_file.read(1)
                return 0
            next_character = self.def_file.read(1)
            if next_character == '':
                return 1
            if next_character == '/':
                return 1
            while self.current_character != "*" or next_character != "/":
                self.current_character = next_character
                next_character = self.def_file.read(1)
                if next_character == '':
                    return 1
            self.current_character = self.def_file.read(1)
            return 0
        else:
            return 1

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol.

        Returns:
        Symbol symbol
        """
        symbol = Symbol()
        sym = self._get_next_symbol()
        symbol.pos = self.def_file.tell() - 1
        [symbol.id] = self.names.lookup([sym])
        if sym is None or sym == '#':  # if broken comment,
            # send EOF signal to stop parsing
            symbol.type = self.EOF
        elif sym == ":":
            symbol.type = self.COLON
        elif sym == ";":
            symbol.type = self.SEMICOLON
        elif sym == ",":
            symbol.type = self.COMMA
        elif sym == "=":
            symbol.type = self.EQUALS
        elif sym == ".":
            symbol.type = self.DOT
        elif sym == "(":
            symbol.type = self.LEFT
        elif sym == ")":
            symbol.type = self.RIGHT
        elif sym == "-":
            symbol.type = self.DASH
        elif sym == "$":
            symbol.type = None  # Unknown character

        # Symbol can now be only alphanumeric so either
        #  <NAME> <KEYWORD> <LOGICTYPE> or <CONFVAR>
        elif sym in self.device_list:
            symbol.type = self.LOGICTYPE
        elif sym in self.keywords_list:
            symbol.type = self.KEYWORD
        else:
            try:
                if int(sym) == int(sym):  # need to check if can convert to int
                    symbol.type = self.CONFVAR
            except ValueError:
                symbol.type = self.NAME
                return symbol

        return symbol

    def print_error(self, error_index):
        """
        Prints the line number, the line containing the error , and a caret
        under the error

        Returns:
        A string containing the line number the line containing the error,
        and a caret under the error, to be parsed to the gui
        """
        error_handling_text = self._open_file(self.path)
        error_handling_text.seek(0, 0)
        # Record number of end lines
        lines = 0
        line_index = 0
        tabs = 0
        if error_index is None:
            return ""
        for i in range(error_index):
            next_byte = error_handling_text.read(1)
            if next_byte == '\n':
                lines += 1
                line_index = error_handling_text.tell() + 1

        # print(lines + 1, error_index - line_index)
        line_str = _("Line: ")
        print(line_str, lines + 1)
        error_handling_text.seek(0)
        error_line = error_handling_text.readlines()[lines]
        # Record the number of tabs in error_line before character of interest
        err_line_before = error_line[:(error_index - line_index)]
        for letter in err_line_before:
            if letter == '\t':
                tabs += 1
        # Check for tabs and replace with 4 spaces if any presents
        error_line = error_line.replace('\t', "".ljust(4))
        print(error_line, end="")
        # if error_index == line_index:
        #     print("^")
        # else:
        emptystring = ''.ljust(error_index - line_index + tabs * 3) + '^'
        print(emptystring)
        return line_str + str(lines + 1) + '\n' + error_line +\
            '\n' + emptystring + '\n'
