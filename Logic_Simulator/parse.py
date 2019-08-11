"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from scanner import Symbol
import wx
import builtins
builtins.__dict__['_'] = wx.GetTranslation


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.

    Private methods
    --------------
    _error(self, error_type, stopping_symbol_set): Report errors and skip to
                                                   first stopping symbol.

    _name(self): Check for syntax errors in 'name' rule.

    _configvar(self): Check for syntax errors in 'configvar' rule.

    _config_list(self): Check for syntax errors in 'config_list' rule.

    _logictype(self): Check for syntax errors in 'logictype' rule.

    _dev(self): Check for syntax and semantic errors in 'dev' rule.

    _dev_block(self): Check for syntax errors in 'dev_block' rule.

    _port(self): Check for syntax errors in 'port' rule.

    _signame(self): Check for syntax errors in 'signame' rule.

    _con(self): Check for syntax and semantic errors in 'con' rule.

    _con_block(self): Check for syntax errors in 'con_block' rule.

    _mon(self): Check for syntax errors in 'mon_block' rule.

    _mon_block(self): Check for syntax errors in 'mon_block' rule.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.symbol = Symbol()
        self.error_count = 0    # Total error count of errors during parsing
        self.err_flag = False   # Indicates comma/semicolon is stopping symbol

        # Global record of all possible errors
        [self.NO_DEVICES, self.NO_CONNECTIONS, self.NO_MONITORS, self.NO_END,
         self.NO_COLON, self.NO_COMMA, self.NO_SEMICOLON, self.NO_EQUALS,
         self.NO_NUMBER, self.NO_STRING, self.INVALID_LOGIC,
         self.NO_LEFTBRACKET, self.NO_RIGHTBRACKET,
         self.NO_EOF, self.UNUSED_INPUTS] = self.names.unique_error_codes(15)

        # Populate occurrence of all errors in list for easy testing
        self.reported_errs = []

        # Logic types with configuration variables
        self.log_types_vars = ['CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR',
                               'SIGGEN']

        # Printing of errors to GUI
        self.print_gui = []

        # Store previous symbol
        self.prev_sym = Symbol()
        self.prev_sym.pos = 1  # EOF Error adjustment
        self.flag_prev_sym = False

        # Store an older and current symbol for dealing with semantic errors
        self.old_symbol = Symbol()
        self.old_symbol.pos = 1  # EOF Error adjustment
        self.older_symbol = Symbol()
        self.older_symbol.pos = 1  # EOF Error adjustment
        self.curr_symbol = Symbol()
        self.curr_symbol.pos = 1  # EOF Error adjustment
        self.flag_old_sym = False

    def _error(self, error_type, stopping_symbol_set):
        """Report errors and skip to first stopping symbol.

        Store a record of all error messages in order to print to GUI log.
        """
        self.reported_errs.append(error_type)
        # Print line with location of error
        self.print_gui.append(self.scanner.print_error(self.symbol.pos))
        self.error_count += 1
        # Report error message and append to error list.
        msg = None
        if error_type == self.NO_DEVICES:
            msg = _("***ERROR: Expected DEVICES keyword")
        if error_type == self.NO_CONNECTIONS:
            msg = _("***ERROR: Expected CONNECTIONS keyword")
        if error_type == self.NO_MONITORS:
            msg = _("***ERROR: Expected MONITORS keyword")
        if error_type == self.NO_END:
            msg = _("***ERROR: Expected END keyword")
        if error_type == self.NO_EOF:
            msg = _("***ERROR: Expected End Of File")
        if error_type == self.NO_COLON:
            msg = _("***ERROR: Expected a colon")
        if error_type == self.NO_COMMA:
            msg = _("***ERROR: Expected a comma")
        if error_type == self.NO_SEMICOLON:
            msg = _("***ERROR: Expected a semicolon")
        if error_type == self.NO_EQUALS:
            msg = _("***ERROR: Expected an equals symbol")
        if error_type == self.NO_NUMBER:
            msg = _("***ERROR: Expected a positive integer or 0")
        if error_type == self.NO_STRING:
            msg = _("***ERROR: Expected a string of characters not including "
                    "reserved words")
        if error_type == self.INVALID_LOGIC:
            msg = _("***ERROR: Expected logic types CLOCK, SWITCH, AND, NAND, "
                    "NOR, OR, DTYPE, SIGGEN or XOR")
        if error_type == self.NO_LEFTBRACKET:
            msg = _("***ERROR: Expected a left bracket")
        if error_type == self.NO_RIGHTBRACKET:
            msg = _("***ERROR: Expected a right bracket")
        if error_type == self.devices.INVALID_QUALIFIER:
            msg = _("***ERROR: Invalid configuration variable")
        if error_type == self.devices.NO_QUALIFIER:
            msg = _("***ERROR: Expected configuration variable")
        if error_type == self.devices.BAD_DEVICE:
            msg = _("***ERROR: Expected logic types CLOCK, SWITCH, AND, NAND, "
                    "NOR, OR, DTYPE or XOR")
        if error_type == self.devices.QUALIFIER_PRESENT:
            msg = _("***ERROR: Did not expect configuration variable")
        if error_type == self.devices.DEVICE_PRESENT:
            msg = _("***ERROR: Device already defined")
        if error_type == self.devices.TOO_MANY_QUALIFIER:
            msg = _("***ERROR: Too many configuration variables specified")
        if error_type == self.devices.INVALID_QUALIFIER_LIST:
            msg = _("***ERROR: Invalid configuration variables used - "
                    "only 0s and 1s accepted")
        if error_type == self.network.INPUT_TO_INPUT:
            msg = _("***ERROR: Input is connected to an input")
        if error_type == self.network.OUTPUT_TO_OUTPUT:
            msg = _("***ERROR: Output is connected to an output")
        if error_type == self.network.INPUT_CONNECTED:
            msg = _("***ERROR: Input has already been connected")
        if error_type == self.network.PORT_ABSENT:
            msg = _("***ERROR: Port is absent")
        if error_type == self.network.DEVICE_ABSENT:
            msg = _("***ERROR: Device is absent")
        if error_type == self.monitors.NOT_OUTPUT:
            msg = _("***ERROR: Only monitor outputs")
        if error_type == self.monitors.MONITOR_PRESENT:
            msg = _("***ERROR: Output has already been monitored")
        if error_type == self.UNUSED_INPUTS:
            msg = _("***ERROR: Unused inputs in file definition")
        print(msg)
        msg = msg + '\n' + "---------" + '\n'
        self.print_gui.append(msg)
        # After an error is detected, skip symbols up till the
        # appropriate stopping symbol
        if self.flag_old_sym:
            # Semantic error was raised and must be corrected
            self.symbol = self.curr_symbol
            self.flag_old_sym = False
        if self.flag_prev_sym:
            # Do not go to next line captured
            self.symbol = self.curr_symbol
            self.flag_prev_sym = False
        while (not(self.symbol.type in stopping_symbol_set) and
                self.symbol.type != self.scanner.EOF):
            self.symbol = self.scanner.get_symbol()
        # If stopping symbol is a comma or a semicolon, a
        # special flag is raised
        if (self.symbol.type == self.scanner.COMMA or
                self.symbol.type == self.scanner.SEMICOLON):
            self.err_flag = True
        else:
            self.err_flag = False

    def _name(self):
        """Check for syntax errors in 'name' rule.

        Return ID of device being checked. Return None if error in device.
        """
        device_id = None
        if self.symbol.type == self.scanner.NAME:
            device_str = self.names.get_name_string(self.symbol.id)
            device_id = self.names.query(device_str)
            self.symbol = self.scanner.get_symbol()
        else:
            # Expected a string
            self._error(self.NO_STRING, [self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
            self.err_flag = False
        return device_id

    def _configvar(self):
        """Check for syntax errors in 'configvar' rule.

        Return device configuration variable. Return None if none specified.
        """
        device_property = None
        if self.symbol.type == self.scanner.CONFVAR:
            device_property = int(self.names.get_name_string(self.symbol.id))
            self.symbol = self.scanner.get_symbol()
        else:
            # Expected an integer
            self._error(self.NO_NUMBER, [self.scanner.RIGHT,
                                         self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
        return device_property

    def _config_list(self):
        """Check for syntax errors in 'config_list' rule.

        Return device configuration list. Return None if none specified.
        """
        device_property_list = []
        device_property_list.append(self._configvar())
        while self.symbol.type == self.scanner.DASH:
            self.symbol = self.scanner.get_symbol()
            device_property_list.append(self._configvar())
        return device_property_list

    def _logictype(self):
        """Check for syntax errors in 'logictype' rule.

        Return the string for the device type and integer code for the device
        type.
        """
        device_str = None
        device_kind = None
        if self.symbol.type == self.scanner.LOGICTYPE:
            device_str = self.names.get_name_string(self.symbol.id)
            device_kind = self.names.query(device_str)
            self.symbol = self.scanner.get_symbol()
        else:
            # Allowable logic types are only CLK, SWC,
            # AND, NAND, NOR, OR, DTYPE, XOR
            self._error(self.INVALID_LOGIC, [self.scanner.EQUALS,
                                             self.scanner.COMMA,
                                             self.scanner.SEMICOLON])
        return [device_str, device_kind]

    def _dev(self):
        """Check for syntax and semantic errors in 'dev' rule.

        Check for semantic errors only if no errors are present in the device.
        """
        device_property = None
        [device_str, device_kind] = self._logictype()
        # Flag is only raised if stopping symbol is comma or semicolon
        if self.err_flag:
            self.err_flag = False
            return
        # Configuration variables are optional
        if self.symbol.type == self.scanner.LEFT:
            self.symbol = self.scanner.get_symbol()
            self.old_symbol = self.symbol
            device_property = self._config_list()
            # Skip to closest comma or semicolon in case major error occurs
            if self.err_flag:
                self.err_flag = False
                return
            if self.symbol.type == self.scanner.RIGHT:
                self.symbol = self.scanner.get_symbol()
            else:
                # Missing right bracket symbol
                self._error(self.NO_RIGHTBRACKET, [self.scanner.EQUALS,
                                                   self.scanner.COMMA,
                                                   self.scanner.SEMICOLON])
                # Reset flag
                if self.err_flag:
                    self.err_flag = False
                    return
        elif device_str in self.log_types_vars:
            if self.symbol.type == self.scanner.EQUALS:
                # Missing qualifier
                self._error(self.devices.NO_QUALIFIER,
                            [self.scanner.EQUALS,
                             self.scanner.COMMA,
                             self.scanner.SEMICOLON])
            else:
                # Missing Left bracket
                self._error(self.NO_LEFTBRACKET, [self.scanner.EQUALS,
                                                  self.scanner.COMMA,
                                                  self.scanner.SEMICOLON])
            # Reset flag
            if self.err_flag:
                self.err_flag = False
                return
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.older_symbol = self.symbol
            device_id = self._name()
        else:
            # Missing equals symbol
            self._error(self.NO_EQUALS, [self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
            self.err_flag = False
        if self.error_count == 0:
            error_type = self.devices.make_device(device_id, device_kind,
                                                  device_property)
            if error_type != self.devices.NO_ERROR:
                # Point error to correct position
                self.curr_symbol = self.symbol
                if error_type == self.devices.DEVICE_PRESENT:
                    self.symbol = self.older_symbol
                else:
                    self.symbol = self.old_symbol
                self.flag_old_sym = True
                self._error(error_type, [self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
                self.err_flag = False

    def _dev_block(self):
        """Check for syntax errors in 'dev_block' rule."""
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.DEVICES_ID):
            self.prev_sym = self.symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
                # Must have at least one device
                self._dev()
            else:
                # Missing colon
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_COLON, [self.scanner.COMMA,
                                            self.scanner.SEMICOLON])
                self.err_flag = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._dev()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            elif self.symbol.type == self.scanner.KEYWORD:
                # Missing semicolon
                self.curr_symbol = self.symbol
                self.symbol = self.older_symbol
                self.flag_old_sym = True
                self._error(self.NO_SEMICOLON, [self.scanner.KEYWORD])
            else:
                # Missing comma
                self.curr_symbol = self.symbol
                self.symbol = self.older_symbol
                self.flag_old_sym = True
                self._error(self.NO_COMMA, [self.scanner.KEYWORD])
        else:
            # Missing DEVICES keyword
            self._error(self.NO_DEVICES, [self.scanner.KEYWORD])

    def _port(self):
        """Check for syntax errors in 'port' rule.

        Return integer code for port. Return None if error in port defintion.
        """
        port_id = None
        if self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            self.prev_sym = self.symbol
            port_id = self._name()
        return port_id

    def _signame(self):
        """Check for syntax errors in 'signame' rule.

        Return integer codes for port and the device. Return None for both if
        error in device definition.
        """
        device_id = None
        port_id = None
        if self.symbol.type == self.scanner.NAME:
            device_str = self.names.get_name_string(self.symbol.id)
            device_id = self.names.query(device_str)
            self.prev_sym = self.symbol
            self.symbol = self.scanner.get_symbol()
            port_id = self._port()
        else:
            # Expected string
            self._error(self.NO_STRING, [self.scanner.EQUALS,
                                         self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
        return [device_id, port_id]

    def _con(self):
        """Check for syntax and semantic errors in 'con' rule.

        Check for semantic errors only if no errors are present in the
        connection.
        """
        [in_device_id, in_port_id] = self._signame()
        # Reset comma and semicolon stopping symbol flag
        if self.err_flag:
            self.err_flag = False
            return
        if self.symbol.type == self.scanner.EQUALS:
            self.old_symbol = self.symbol
            self.symbol = self.scanner.get_symbol()
            self.older_symbol = self.symbol
            [out_device_id, out_port_id] = self._signame()
        else:
            # Missing equals symbol
            self._error(self.NO_EQUALS, [self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
            self.err_flag = False
        if self.error_count == 0:
            # Construct network if no semantic or syntax errors
            error_type = self.network.make_connection(in_device_id, in_port_id,
                                                      out_device_id,
                                                      out_port_id)
            if error_type != self.network.NO_ERROR:
                # Point error to correct position
                self.curr_symbol = self.symbol
                if(error_type == self.network.INPUT_CONNECTED or
                   error_type == self.network.PORT_ABSENT):
                    self.symbol = self.prev_sym
                    self.flag_prev_sym = True
                else:
                    self.symbol = self.old_symbol
                    self.flag_old_sym = True
                self._error(error_type, [self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
                self.err_flag = False

    def _con_block(self):
        """Check for syntax errors in 'con_block' rule."""
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.CONNECT_ID):
            self.prev_sym = self.symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
                # Must have at least one connection
                self._con()
            else:
                # Missing colon
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_COLON, [self.scanner.COMMA,
                                            self.scanner.SEMICOLON])
                self.err_flag = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._con()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            elif self.symbol.type == self.scanner.KEYWORD:
                # Missing semicolon
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_SEMICOLON, [self.scanner.KEYWORD])
            else:
                # Missing comma
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_COMMA, [self.scanner.KEYWORD])
        else:
            # Missing CONNECTIONS keyword
            self._error(self.NO_CONNECTIONS, [self.scanner.KEYWORD])

    def _mon(self):
        """Check for syntax errors in 'mon_block' rule.

        Check for semantic errors only if no errors are present in the
        monitoring point.
        """
        [device_id, output_id] = self._signame()
        if self.error_count == 0:
            # Set monitoring points if no syntax or semantic errors
            error_type = self.monitors.make_monitor(device_id, output_id)
            if error_type != self.monitors.NO_ERROR:
                self._error(error_type, [self.scanner.COMMA,
                                         self.scanner.SEMICOLON])
                self.err_flag = False

    def _mon_block(self):
        """Check for syntax errors in 'mon_block' rule."""
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.MONITOR_ID):
            self.prev_sym = self.symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
                # Must have at least one monitoring point
                self._mon()
            else:
                # Missing colon
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_COLON, [self.scanner.COMMA,
                                            self.scanner.SEMICOLON])
                self.err_flag = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self._mon()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            elif self.symbol.type == self.scanner.KEYWORD:
                # Missing semicolon
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_SEMICOLON, [self.scanner.KEYWORD])
            else:
                # Missing comma
                self.curr_symbol = self.symbol
                self.symbol = self.prev_sym
                self.flag_prev_sym = True
                self._error(self.NO_COMMA, [self.scanner.KEYWORD])
        else:
            # Missing MONITORS keyword
            self._error(self.NO_MONITORS, [self.scanner.KEYWORD])

    def parse_network(self):
        """Parse the circuit definition file.

        Return True if parsing successful with no errors and False otherwise.
        """
        # Get first symbol in file
        self.symbol = self.scanner.get_symbol()
        self._dev_block()
        self._con_block()
        self._mon_block()
        if (not(self.network.check_network()) and self.error_count == 0):
            # Raise unused inputs semantic error
            self._error(self.UNUSED_INPUTS, [self.scanner.KEYWORD])
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.END_ID):
            self.symbol = self.scanner.get_symbol()
            if not(self.symbol.type == self.scanner.EOF):
                # Missing EOF
                self._error(self.NO_EOF, [])
        else:
            # Missing END keyword
            self._error(self.NO_END, [])
        if self.error_count == 0:
            return True
        else:
            msg = ("\n" + _("Total number of errors: ") +
                   str(self.error_count) + "\n")
            print(msg)
            self.print_gui.append(msg)
            return False
