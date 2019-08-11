"""Test scanner module"""
import pytest
import os
from scanner import Scanner, Symbol
from names import Names


@pytest.fixture
def names():
    a = Names()
    return a


def test_open_file_(names):
    """Test file open within scanner.py"""
    f = open('test_specfiles/test_scanner/test_open_file.txt')
    scanner = Scanner('test_specfiles/test_scanner/test_open_file.txt', names)
    f1 = scanner._open_file(scanner.path)
    assert f.read() == f1.read()


def test_remove_spaces(names):
    """Test spaces in a file removed"""
    scanner = Scanner(
        'test_specfiles/test_scanner/test_remove_spaces.txt', names)
    # Function should advance to next non space character.
    scanner._remove_spaces()
    assert scanner.current_character == 'D'


def test_get_next_symbol(names):
    """Test specific symbol is scanned correctly"""
    scanner = Scanner(
        'test_specfiles/test_scanner/test_get_next_symbol.txt', names)
    # Assert name read correctly
    symbol_next = scanner._get_next_symbol()
    assert symbol_next == 'DEVICES'
    # Assert unrecognised character read correctly
    symbol_next = scanner._get_next_symbol()
    assert symbol_next == '$'
    # Assert EOF character read correctly
    symbol_next = scanner._get_next_symbol()
    symbol_next = scanner._get_next_symbol()
    assert symbol_next is None


def test_get_symbol(names):
    """Test different symbol types are registered correctly"""
    scanner = Scanner('test_specfiles/test_scanner/test_get_symbol.txt',
                      names)
    # Each case has symbol type reference and
    # position in file.
    test_cases = [
        (scanner.KEYWORD, 7),
        (None, 8),
        (scanner.LOGICTYPE, 13),
        (scanner.LEFT, 15),
        (scanner.CONFVAR, 16),
        (scanner.RIGHT, 17),
        (scanner.NAME, 27)
    ]
    # Call getsymbol to advance to next symbol
    # before assertion.
    for i in range(7):
        symbol = scanner.get_symbol()
        assert symbol.type == test_cases[i][0]
        assert symbol.pos == test_cases[i][1]


def test_remove_comment(names):
    """
    Test whether different types of comments
    can be removed correctly
    """
    # Edited test_remove_comment.txt
    # to reflect bug fix in scanner.py
    # test_remove_comment.txt contains different comment
    # instances interspaced by symbols refrenced below.
    scanner = Scanner(
        'test_specfiles/test_scanner/test_remove_comment.txt', names)
    assert scanner.get_symbol().type == scanner.LOGICTYPE
    assert scanner.get_symbol().type == scanner.EQUALS
    assert scanner.get_symbol().type == scanner.NAME
    assert scanner.get_symbol().type == scanner.LOGICTYPE


def test_print_error(names):
    """Tests whether an error is printed correctly"""
    scanner = Scanner(
        'test_specfiles/test_scanner/test_print_error.txt', names)
    # Test whether carrot prints correctly when error index
    # 5 is passed.
    outp = scanner.print_error(5)
    assert outp == 'Line: 1\nDEVICES* CONNECTIONS\n     ^\n'
