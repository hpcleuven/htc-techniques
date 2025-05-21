#!/usr/bin/env python3

import os
import sys
import argparse
import re
from matplotlib import pyplot as plt


REG_TIMINGS = re.compile(
                         r'^(?P<KEY>[\w\_]+)=(?P<VAL>[\d]+)\n'
                         r'^\[\d+\]\s([-+eE0-9.]+)\s+([-+eE0-9.]+)\n\n'
                         r'^real\s+(?P<REAL>[\d\w\.]+)\n'
                         r'^user\s+(?P<USER>[\d\w\.]+)\n'
                         r'^sys\s+(?P<SYS>[\d\w\.]+)\n'
                         , re.MULTILINE)

REG_MINSEC = re.compile(r'(?P<MIN>[\d]+)m(?P<SEC>[\d\.]+)s')


def parse_args():
    """ Parse command line args """
    parser = argparse.ArgumentParser(prog='plotter.py',
                description='Plotter for benchmarking results')
    parser.add_argument('-f', '--filename', help='logfile containing scaling results')

    return parser.parse_args()


def convert_to_sec(minsec):
    """
    Convert a string like '1m31.45s' to seconds (float)

    Parameters
    ----------
    minsec: str, minute and seconds (output of `time` command)

    Returns
    -------
    secs: float, elapsed time in seconds
    """
    match = re.match(REG_MINSEC, minsec)
    assert match is not None, f'ERROR: REG_MINSEC could not match "{minsec}"'
    min, sec = float(match['MIN']), float(match['SEC'])

    return 60. * min + sec


def read_and_parse_filename(fname):
    """
    Read the input scaling file and parse the key-value pairs
    and the elapsed (real) time from the file

    Parameters
    ----------
    fname: str; full/relative path to the input file

    Returns
    -------
    """
    if not os.path.exists(fname):
        raise FileNotFoundError(f'Failed to find {fname}')

    with open(fname, 'r') as fh:
        lines = fh.readlines()    # list of str
        lines = ''.join([l for l in lines if not l.startswith('Loading required package:')])    # str

    blocks = re.findall(REG_TIMINGS, lines)
    assert blocks is not None, 'ERROR: re.findall failed for REG_TIMINGS pattern'
    assert len(blocks) > 1, 'ERROR: re.findall is expected to find more than one match'

    for block in blocks:
        key, val = block[0], block[1]
        val = int(val)
        real, user, sys = block[4:7]
        real = convert_to_sec(real)
        user = convert_to_sec(user)
        sys  = convert_to_sec(sys)

        print(key, val, real, user, sys)

def main():
    """ The main caller """
    args = parse_args()

    data = read_and_parse_filename(args.filename)

if __name__ == '__main__':
    sys.exit(main())
