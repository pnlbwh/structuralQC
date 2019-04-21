import numpy as np
import configparser
from os.path import abspath, dirname, join as pjoin

SCRIPTDIR= abspath(dirname(__file__))
config = configparser.ConfigParser()
config.read(pjoin(SCRIPTDIR, 'config.ini'))
POINTS= int(config['DEFAULT']['POINTS'])

def extract_feature(volume):

    volume= volume.flatten( )

    sig = np.median(abs(volume - np.median(volume))) / 0.6745

    N = len(volume)
    # Estimate bandwidth
    if sig > 0:
        h = sig * (4 / (3 * N)) ** 0.2
    else:
        h = 1

    # Calculate data points where we want to find ksdensity estimate
    e1 = volume.min() - h * 3
    e2 = volume.max() + h * 3

    x = np.linspace(e1, e2, POINTS)
    x = np.array(x).reshape(1, POINTS)

    volume = np.array(volume).reshape(len(volume), 1)
    volumeMatrix = np.repeat(volume, POINTS, axis=1)
    temp = (x - volumeMatrix) / h
    Z = np.sum(np.exp(-0.5 * temp ** 2), axis=0)

    final = Z / sum(Z)

    return final