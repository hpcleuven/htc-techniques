#!/usr/bin/env python3

import sys
import argparse
from subprocess import run, PIPE
import numpy as np
from matplotlib import pyplot as plt


BASE_LOG_XAXIS = 2


def parse_args():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser(prog='worker_analyzer.py')
    parser.add_argument('-j', '--job-ids', type=str, 
                        help='Comma-separated list of JobIDs to retrieve worker information from')
    parser.add_argument('-n', '--ntasks', type=str,
                        help='Comma-separated list of tasks for the jobs (in the same order)')
    parser.add_argument('-t', '--tabulate', action='store_true',
                        help='Tabulate scaling results')
    parser.add_argument('--plot-runtime', action='store_true',
                        help='Plot the walltime (runtime) for all worker items')
    parser.add_argument('--plot-speedup', action='store_true',
                         help='Plot only the speedup results')
    parser.add_argument('--plot-efficiency', action='store_true',
                         help='Plot only the parallel efficiency results')
    parser.add_argument('-f', '--figure-name', help='Full/relative path to the figure name')

    return parser.parse_args()


def analyze(jobids, ntasks):
    """
    Analyze the jobs

    Parameters
    ----------
    jobids : list
    ntasks : list of int, number of tasks corresponding to the jobids

    Returns
    -------
    dics : list of dics, keywords are: id, walltime (sec), ntasks, speedup, efficiency
    """
    dics = list()
    for id, jobid in enumerate(jobids):
       cmd = 'slurm_jobinfo %s | grep "Used walltime"' % jobid
       proc = run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf-8')
       assert proc.returncode == 0, f'Running {cmd} failed'
       assert not proc.stderr, f'STDERR: {proc.stderr}'
       stdout = proc.stdout
       walltime = stdout.split(' ')[-1]
       hr, min, sec = walltime.split(':')
       wt_sec = int(sec) + 60*int(min) + 3600*int(hr)
       d = {'id': id, 'walltime': wt_sec, 'ntasks':ntasks[id]}
       dics.append(d)

    baseline = [d for d in dics if d['ntasks'] == 1][0]  # dict
    baseline_sec = baseline['walltime']

    for id, d in enumerate(dics):
        d['speedup'] = baseline_sec / d['walltime']
        d['efficiency'] = d['speedup'] / d['ntasks']

    return dics


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
    key = 'Concurrency'
    lines = [f'| {key:11s} | RUNTIME | SPEEDUP | EFF.  |\n',
             '|-------------|---------|---------|-------|\n']
    for d in dics:
        ntasks = d['ntasks']
        walltime = d['walltime']
        speedup = d['speedup']
        efficiency = d['efficiency']
        line = f'| {ntasks:<11d} | {walltime:<7.1f} | {speedup:<7.1f} | {efficiency:<5.3f} |\n'
        lines.append(line)

    return lines


def plot_runtime(dics, name='plot.png'):
     """
     Plot the pure runtime (s) base on the 'walltime' key in each dict against number of
     worker items running on the node (which is represented by '--ntasks')

     Parameters
     ----------
     dics: list of dict; see 'analyze()'
     name: str, absolute/relative path to the figure name
     """
     xvals = [d['ntasks'] for d in dics]
     yvals = [d['walltime'] for d in dics]

     fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

     plt.plot(xvals, yvals, color='b', marker='o', markersize=14, linestyle='-', linewidth=3)
     ax.set_xticks(ticks=np.log2(xvals))
     ax.set_xticklabels([str(x) for x in xvals])
     ax.set_xscale('log', base=BASE_LOG_XAXIS)
     plt.xlabel('Num Concurrent Worker Items', fontsize='large')
     plt.ylabel('Total Walltime (sec)', fontsize='large')

     fig.tight_layout()
     plt.savefig(name, transparent=True)


def plot_speedup(dics, name='plot.png'):
    """
    Plot the speedup

    Parameters
    ----------
    dics: list of dict; see 'do_benchmark()'
    name: str, absolute/relative path to the figure name
    """
    xvals = [d['ntasks'] for d in dics]
    yvals  = [d['speedup'] for d in dics]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    ax.plot(xvals, xvals, linestyle='solid', linewidth=3, color='grey', zorder=0)
    ax.plot(xvals, yvals, color='b', marker='o', markersize=14, linestyle='-', linewidth=3, zorder=1)
    ax.set_xlabel('Num Concurrent Worker Items', fontsize='large')
    ax.set_xscale('log', base=BASE_LOG_XAXIS)
    ax.set_ylabel('Speedup', fontsize='large')

    fig.tight_layout()
    fig.savefig(name, transparent=True)


def plot_efficiency(dics, name='plot.png'):
    """
    Plot the parallel efficiency

    Parameters
    ----------
    dics: list of dict; see 'do_benchmark()'
    name: str, absolute/relative path to the figure name
    """
    xvals = [d['ntasks'] for d in dics]
    yvals  = [d['efficiency'] for d in dics]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    ax.plot(xvals, yvals, color='r', marker='o', markersize=14, linestyle='-', linewidth=3, zorder=0)
    ax.set_xlabel('Num Concurrent Worker Items', fontsize='large')
    ax.set_ylabel('Efficiency', fontsize='large')
    ax.set_xscale('log', base=BASE_LOG_XAXIS)

    fig.tight_layout()
    fig.savefig(name, transparent=True)


def main():
    args = parse_args()
    jobids = args.job_ids.split(',')
    ntasks = args.ntasks.split(',')
    ntasks = [int(ntask) for ntask in ntasks]
    assert len(jobids) == len(ntasks), 'The sizes of JobIDs and ntasks do not match'

    dics = analyze(jobids, ntasks)

    if args.tabulate:
        table = tabulate(dics)
        print(''.join(table))

    if args.plot_runtime:
        plot_runtime(dics, args.figure_name)

    if args.plot_speedup:
        plot_speedup(dics, args.figure_name)

    if args.plot_efficiency:
        plot_efficiency(dics, args.figure_name)

    return 0


if __name__ == '__main__':
    sys.exit(main())
