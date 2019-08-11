import pytest

from scanner import Scanner
from parse import Parser
from devices import Devices
from names import Names
from network import Network
from monitors import Monitors


#
@pytest.fixture
def create_parser(input_file):
    """Return a new parser instance."""
    path = "./test_specfiles/test_parse/" + input_file
    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    return Parser(names, devices, network, monitors, scanner)


@pytest.mark.parametrize("input_file, errors,  success", [
    ("circuit1_specfile.txt", [], True),
    ("circuit2_specfile.txt", ["create_parser.NO_DEVICES"], False),
    ("circuit3_specfile.txt", ['create_parser.NO_CONNECTIONS'], False),
    ("circuit4_specfile.txt", ['create_parser.NO_MONITORS'], False),
    ("circuit5_specfile.txt", ['create_parser.NO_END'], False),
    ("circuit6_specfile.txt", ['create_parser.NO_COLON',
                               'create_parser.NO_COLON',
                               'create_parser.NO_COLON'], False),
    ("circuit7_specfile.txt", ['create_parser.NO_COMMA',
                               'create_parser.NO_COMMA',
                               'create_parser.NO_COMMA'], False),
    ("circuit8_specfile.txt", ['create_parser.NO_SEMICOLON',
                               'create_parser.NO_SEMICOLON',
                               'create_parser.NO_SEMICOLON'], False),
    ("circuit9_specfile.txt", ['create_parser.NO_EQUALS',
                               'create_parser.NO_EQUALS'], False),
    ("circuit10_specfile.txt", ['create_parser.NO_NUMBER'], False),
    ("circuit11_specfile.txt", ['create_parser.NO_STRING',
                                'create_parser.NO_STRING'], False),
    ("circuit12_specfile.txt", ['create_parser.INVALID_LOGIC',
                                'create_parser.INVALID_LOGIC'], False),
    ("circuit13_specfile.txt", ['create_parser.NO_LEFTBRACKET'], False),
    ("circuit14_specfile.txt", ['create_parser.NO_RIGHTBRACKET',
                                'create_parser.NO_RIGHTBRACKET'], False),
    ("circuit15_specfile.txt", ['create_parser.network.PORT_ABSENT'], False),
    ("circuit16_specfile.txt", ['create_parser.devices.INVALID_QUALIFIER'],
     False),
    ("circuit17_specfile.txt", ['create_parser.devices.NO_QUALIFIER'], False),
    # ("circuit18_specfile.txt", ['create_parser.devices.BAD_DEVICE'],
    #  False),  # Already dealt with in INVALID_LOGIC
    ("circuit19_specfile.txt", ['create_parser.devices.QUALIFIER_PRESENT'],
     False),
    ("circuit20_specfile.txt", ['create_parser.devices.DEVICE_PRESENT'],
     False),
    ("circuit21_specfile.txt", ['create_parser.network.INPUT_TO_INPUT'],
     False),
    ("circuit22_specfile.txt", ['create_parser.network.OUTPUT_TO_OUTPUT'],
     False),
    ("circuit23_specfile.txt", ['create_parser.network.INPUT_CONNECTED'],
     False),
    ("circuit24_specfile.txt", ['create_parser.network.PORT_ABSENT'], False),
    ("circuit25_specfile.txt", ['create_parser.network.DEVICE_ABSENT'], False),
    ("circuit26_specfile.txt", ['create_parser.monitors.NOT_OUTPUT'], False),
    ("circuit27_specfile.txt", ['create_parser.monitors.MONITOR_PRESENT'],
     False),
    ("circuit28_specfile.txt", ['create_parser.devices.TOO_MANY_QUALIFIER'],
     False),
    ("circuit29_specfile.txt",
     ['create_parser.devices.INVALID_QUALIFIER_LIST'],
     False)
])
def test_parse_network(create_parser,  errors,  success):
    """Test if get_string returns the expected string."""
    # Test if parsing has expected output

    assert create_parser.parse_network() == success

    # Test if parser throws expected errors
    for error_id, error in enumerate(errors):
        assert eval(error) == create_parser.reported_errs[error_id]
