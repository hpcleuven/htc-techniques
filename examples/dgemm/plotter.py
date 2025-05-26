#!/usr/bin/env python3

import os
import sys
import argparse
import re
import numpy as np
from matplotlib import pyplot as plt

### Predefined/global consts
REG_TIMINGS = re.compile(
                         r'^(?P<KEY>[\w\_]+)=(?P<VAL>[\d]+)\n'
                         r'^\[\d+\]\s([-+eE0-9.]+)\s+([-+eE0-9.]+)\n\n'
                         r'^real\s+(?P<REAL>[\d\w\.]+)\n'
                         r'^user\s+(?P<USER>[\d\w\.]+)\n'
                         r'^sys\s+(?P<SYS>[\d\w\.]+)\n'
                         , re.MULTILINE)

REG_MINSEC = re.compile(r'(?P<MIN>[\d]+)m(?P<SEC>[\d\.]+)s')

BASE_LOG_XAXIS = 2


### helper functions
def parse_args():
    """ Parse command line args """
    parser = argparse.ArgumentParser(prog='plotter.py',
                description='Plotter for benchmarking results')
    parser.add_argument('-f', '--filename', help='logfile containing scaling results')
    parser.add_argument('-t', '--tabulate', action='store_true', 
                        help='Tabulate the results in Quarto format')
    parser.add_argument('--plot-runtime', action='store_true',
                        help='Plot real runtime (sec)')
    parser.add_argument('--plot-speedup', action='store_true',
                        help='Plot only the speedup results')
    parser.add_argument('--plot-efficiency', action='store_true',
                        help='Plot only the parallel efficiency results')
    parser.add_argument('--plot-scaling', action='store_true',
                        help='Plot both the speedup and parallel efficiency together')
    parser.add_argument('--figure-name', default='plot.png',
                        help='Full/relative path to the figure name (default="plot.png")')
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
    dics: list of dic; each dic with these keys: key, val, real, user, sys
    """
    if not os.path.exists(fname):
        raise FileNotFoundError(f'Failed to find {fname}')

    with open(fname, 'r') as fh:
        lines = fh.readlines()    # list of str
        lines = ''.join([l for l in lines if not l.startswith('Loading required package:')])    # str

    blocks = re.findall(REG_TIMINGS, lines)
    assert blocks is not None, 'ERROR: re.findall failed for REG_TIMINGS pattern'
    assert len(blocks) > 1, 'ERROR: re.findall is expected to find more than one match'

    dics = []
    for block in blocks:
        key, val = block[0], block[1]
        val = int(val)
        real, user, sys = block[4:7]
        real = convert_to_sec(real)
        user = convert_to_sec(user)
        sys  = convert_to_sec(sys)

        dics.append({'key': key, 'val': val, 'real': real, 'user': user, 'sys': sys})

    return dics


def do_benchmark(dics):
    """
    Extend the list of dictionaries with speedup and parallel efficiency

    Parameters
    ----------
    dics: list of dics; see `read_and_parse_filename()`
    
    Returns
    -------
    dics: list of dics; extended by two new keys: 'speedup' and 'efficiency'
    """
    baseline = dics[0]
    assert isinstance(baseline, dict), 'ERROR: Unexpected input type'
    base_n = baseline['val']
    base_t = baseline['real']

    extended = []
    for d in dics:
        n = d['val']
        t = d['real']
        d['speedup'] = base_t / t
        d['efficiency'] = d['speedup'] / n
        extended.append(d)

    return extended


def tabulate(dics):
    """
    Print a nicely-formatted table to stdout

    Parameters
    ----------
    dics: list of dict; see `do_benchmark()`
    
    Returns
    -------
    lines: list of str; ready to be printed
    """
    key = dics[0]['key'].upper()
    lines = [f'| {key:7s} | RUNTIME | SPEEDUP | EFF.  |\n',
             '|---------|---------|---------|-------|\n']
    for d in dics:
        val = d['val']
        real = d['real']
        speedup = d['speedup']
        efficiency = d['efficiency']
        line = f'| {val:<7d} | {real:<7.1f} | {speedup:<7.1f} | {efficiency:<5.3f} |\n'
        lines.append(line)

    return lines


def plot_runtime(dics, name='plot.png'):
    """
    Plot the pure runtime (s) base on the 'real' key in each dict

    Parameters
    ----------
    dics: list of dict; see 'do_benchmark()'
    name: str, absolute/relative path to the figure name
    """
    xvals = [d['val'] for d in dics]
    yvals = [d['real'] for d in dics]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    plt.plot(xvals, yvals, color='b', marker='o', markersize=14, linestyle='-', linewidth=3)
    ax.set_xticks(ticks=np.log2(xvals))
    ax.set_xticklabels([str(x) for x in xvals])
    ax.set_xscale('log', basex=BASE_LOG_XAXIS)
    plt.xlabel(dics[0]['key'], fontsize='large')
    plt.ylabel('Runtime (sec)', fontsize='large')

    fig.tight_layout()
    plt.savefig(name, transparent=True)


def plot_scaling(dics, highlight=2, name='plot.png'):
    """
    Plot the speedup and parallel efficiency on top of one another

    Parameters
    ----------
    dics: list of dict; see 'do_benchmark()'
    highlight: int, the datapoint to highlight (default=2)
    name: str, absolute/relative path to the figure name
    """
    xvals = [d['val'] for d in dics]
    ytop  = [d['speedup'] for d in dics]
    ybot  = [d['efficiency'] for d in dics]

    fig, (top, bot) = plt.subplots(2, 1, sharex=True)

    if highlight < len(xvals):
        top.scatter(xvals[highlight], ytop[highlight], s=100, color='black', zorder=1)
        bot.scatter(xvals[highlight], ybot[highlight], s=100, color='black', zorder=1)

    top.plot(xvals, xvals, linestyle='solid', linewidth=3, color='grey')
    top.plot(xvals, ytop, color='b', marker='o', markersize=14, linestyle='-', linewidth=3, zorder=0)
    bot.plot(xvals, ybot, color='r', marker='o', markersize=14, linestyle='-', linewidth=3, zorder=0)
    bot.set_xticks(ticks=xvals, labels=[str(x) for x in xvals])
    bot.set_xlabel(dics[0]['key'], fontsize='large')
    bot.set_xscale('log', basex=BASE_LOG_XAXIS)
    top.set_ylabel('Speedup', fontsize='large')
    bot.set_ylabel('Parallel Efficiency', fontsize='large')

    fig.tight_layout()
    fig.savefig(name, transparent=True)


def plot_speedup(dics, highlight=2, name='plot.png'):
    """
    Plot the speedup

    Parameters
    ----------
    dics: list of dict; see 'do_benchmark()'
    highlight: int, the datapoint to highlight (default=2)
    name: str, absolute/relative path to the figure name
    """
    xvals = [d['val'] for d in dics]
    yvals  = [d['speedup'] for d in dics]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    if highlight < len(xvals):
        ax.scatter(xvals[highlight], yvals[highlight], s=100, color='black', zorder=2)

    ax.plot(xvals, xvals, linestyle='solid', linewidth=3, color='grey', zorder=0)
    ax.plot(xvals, yvals, color='b', marker='o', markersize=14, linestyle='-', linewidth=3, zorder=1)
    ax.set_xlabel(dics[0]['key'], fontsize='large')
    ax.set_xscale('log', basex=BASE_LOG_XAXIS)
    ax.set_ylabel('Speedup', fontsize='large')

    fig.tight_layout()
    fig.savefig(name, transparent=True)


def plot_efficiency(dics, highlight=2, name='plot.png'):
    """
    Plot the parallel efficiency

    Parameters
    ----------
    dics: list of dict; see 'do_benchmark()'
    highlight: int, the datapoint to highlight (default=2)
    name: str, absolute/relative path to the figure name
    """
    xvals = [d['val'] for d in dics]
    yvals  = [d['efficiency'] for d in dics]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    if highlight < len(xvals):
        ax.scatter([xvals[highlight]], [yvals[highlight]], s=100, color='black', zorder=1)

    ax.plot(xvals, yvals, color='r', marker='o', markersize=14, linestyle='-', linewidth=3, zorder=0)
    ax.set_xlabel(dics[0]['key'], fontsize='large')
    ax.set_ylabel('Efficiency', fontsize='large')
    ax.set_xscale('log', basex=BASE_LOG_XAXIS)

    fig.tight_layout()
    fig.savefig(name, transparent=True)


### main caller
def main():
    """ The main caller """
    args = parse_args()

    data = read_and_parse_filename(args.filename)

    benchmark = do_benchmark(data)

    if args.tabulate:
        table = tabulate(benchmark)
        print(''.join(table))

    if args.plot_runtime:
        plot_runtime(dics=benchmark, name=args.figure_name)

    if args.plot_speedup:
        plot_speedup(dics=benchmark, name=args.figure_name)

    if args.plot_efficiency:
        plot_efficiency(dics=benchmark, name=args.figure_name)

    if args.plot_scaling:
        plot_scaling(dics=benchmark, name=args.figure_name)

    return 0


if __name__ == '__main__':
    sys.exit(main())
