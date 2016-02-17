# Copyright (c) 2016 Anders Barth
from __future__ import division
import ctypes
import numpy as np
import warnings
import os

# load shared library
_CCF = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'CCF.so'))


def _CCF_inC(t1, t2, nc, nb, timeaxis):
    """
    Wrapper function to communicate between python and C using ctypes library.
    The returned array yields the correlation of intensity fluctuations, decaying to zero.

    Parameters:

    * t1: Numpy arrays of photon arrival times in channel 1 (integer type)
    * t2: Numpy arrays of photon arrival times in channel 2 (integer type)
    * nc: Number of time points per logarithmic step
    * nb: Number of logarithmic steps
    * timeaxis: Logarithmic timeaxis as defined by nc and nb

    Return:

    * corr_res: 1d array of correlation result

    """
    global _CCF
    # read out number of photons and max time
    np1 = np.size(t1)
    np2 = np.size(t2)
    maxT = np.max([t1[-1], t2[-1]])

    # convert numpy arrays to python lists so they can be converted to ctypes
    w1 = np.ones(np1).tolist()
    w2 = np.ones(np2).tolist()
    t1 = t1.tolist()
    t2 = t2.tolist()
    timeaxis = timeaxis.tolist()

    # initialize output
    zer = np.zeros(len(timeaxis)).tolist()
    corrl = (ctypes.c_double * len(timeaxis))(*zer)

    # call C function with converted data types
    _CCF.CCF((ctypes.c_int64 * np1)(*t1), (ctypes.c_int64 * np2)(*t2),
             (ctypes.c_double * np1)(*w1), (ctypes.c_double * np2)(*w2),
             ctypes.c_int(nc), ctypes.c_int(nb),
             ctypes.c_int(np1), ctypes.c_int(np2),
             (ctypes.c_int * len(timeaxis))(*timeaxis), ctypes.byref(corrl))

    # convert output back to numpy array
    corrl = np.array(corrl)

    # perform normalizing
    divisor = np.ones(np.size(timeaxis), dtype='int')
    divisor[(2 * nc + 1):] = 2 ** (np.floor((np.arange(nc, (np.size(divisor) + 1) - (nc + 2))) / nc))
    corr_res = corrl / divisor / (maxT - timeaxis) / (np1 / t1[-1]) / (np2 / t2[-1]) - 1

    return corr_res


def CCF(t1, t2, nblock=10, nc=10, nb='auto'):
    """
    Performs crosscorrelation of time-tagged photon data t1 and t2 using semi-logarithmic timeaxis
    with nb logarithmic levels and nc equally spaced timebins per level.
    Error estimation is performed by splitting the measurement into nblock time segments of equal length and
    taking the standard error of mean.
    The returned array yields the correlation of intensity fluctuations, decaying to zero.

    Parameters:

    * t1: Numpy arrays of photon arrival times in channel 1 (integer type)
    * t2: Numpy arrays of photon arrival times in channel 2 (integer type)
    * nblock: Number of blocks used for error estimation. (Default: 10)
    * nc: Number of time points per logarithmic level. (Default: 10)
    * nb: Number of logarithmic levels. 'auto' takes the maximum possible lagtime to calculate nb.

    Return:

    * mcorr: 1d array of correlation result
    * stdcorr: Standard error of mean of correlation result
    * timeaxis: Timeaxis

    """

    # Check inputs and convert if feasible
    if not isinstance(t1, np.ndarray):
        t1 = np.array(t1)
        warnings.warn("Input array 1 is not a numpy array, converting...")
    if not isinstance(t2, np.ndarray):
        t2 = np.array(t2)
        warnings.warn("Input array 2 is not a numpy array, converting...")
    if t1.dtype.kind not in ['i', 'u']:
        t1 = t1.astype(int)
        warnings.warn("Input array 1 is not of integer type, converting...")
    if t2.dtype.kind not in ['i', 'u']:
        t2 = t2.astype(int)
        warnings.warn("Input array 2 is not of integer type, converting...")

    # define blocks
    maxT = np.max([t1[-1], t2[-1]])
    blocks = np.linspace(0, np.max([t1[-1], t2[-1]]), nblock + 1).astype(int)

    # preprocess timeaxis
    block_time = np.floor(maxT / nblock)
    if nb is 'auto':
        timeaxis_exponent = np.floor(np.log2(block_time / nc)).astype(int)
        nb = timeaxis_exponent.astype(int)
    else:
        timeaxis_exponent = nb
    timeaxis = np.ones(nc * (timeaxis_exponent + 1))
    timeaxis *= 2 ** np.floor((np.arange(np.size(timeaxis))) / nc - 1)
    timeaxis[timeaxis < 1] = 1
    timeaxis = np.concatenate([np.array([1]), timeaxis])
    timeaxis = np.cumsum(timeaxis).astype(int)

    corr = np.zeros((nblock, np.size(timeaxis)))
    for i in range(nblock):
        corr[i, :] = _CCF_inC(t1[(t1 > blocks[i]) & (t1 <= blocks[i + 1])] - blocks[i],
                              t2[(t2 > blocks[i]) & (t2 <= blocks[i + 1])] - blocks[i],
                              nc, nb, timeaxis)
        # replace -1 occurrences with 0 for time lags that are not realized
        corr[i, (np.size(timeaxis) - np.where(corr[i][::-1] != -1)[0][0]):] = 0
    # remove zeros at end
    valid = np.sum((corr != 0).all(axis=0))
    corr = corr[:, :valid]
    timeaxis = timeaxis[:valid]

    # average and standard deviation
    mcorr = np.mean(corr, axis=0)
    # calculate std on normalized curves!
    corr_norm = np.zeros((nblock, np.size(timeaxis)))
    area = np.sum(corr, axis=1)
    for i in range(np.size(corr, axis=0)):
        corr_norm[i, :] = np.mean(area) * corr[i, :] / area[i]
    stdcorr = np.std(corr_norm, axis=0) / np.sqrt(nblock)

    # first time bin is actually time lag zero, correct for this:
    timeaxis[21:] -= 1

    return mcorr, stdcorr, timeaxis
