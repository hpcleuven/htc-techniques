import argparse
import numpy as np


def parse_arguments():
    """
    Parse cmdargs
    """
    parser = argparse.Argument_Parser(prog='mtrx_pow.py')
    parser.add_argument('-n', '--num-rows', default=500, type='int',
                        help='Number of rows and columns for a square matrix (default=500)')
    parser.add_argument('-e', '--exponent', default=3, type='int',
                        help='Matrix exponent (default=3)')
    
    return parser.parse_args()


def make_mtrx(N):
    """
    Return a N-by-N square matrix of size, with uniform random distribution
    between [-0.5, 0.5)

    Parameters
    ----------
    N : int, number of rows and columns of the array

    Returns
    -------
    mtrx : NxN ndarray of type float
    """
    return np.random.rand(N, N) - 0.5


def exponentiate(A, e):
    """
    Exponentiate the matrix A to the (integer) power 'e', using
    'np.linalg.matrix_power()' function

    Parameters
    ----------
    A : square matrix of float values
    e : int, exponent

    Returns
    -------
    Ae : ndarray
    """
    return np.linalg.matrix_power(A, e)

if __name__ == '__main__':
    args = parse_arguments()

    mtrx = make_mtrx(N=args.num_rows)
    mtrx_e = exponentiate(mtrx, args.exponent)