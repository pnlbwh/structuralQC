import numpy as np
import configparser
from extract_feature import extract_feature
from os.path import abspath, dirname, join as pjoin

SCRIPTDIR= abspath(dirname(__file__))
config = configparser.ConfigParser()
config.read(pjoin(SCRIPTDIR, 'config.ini'))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])


POINTS= int(config['DEFAULT']['POINTS'])

def slide_filter(mri, histName):

    X, Y, Z = np.shape(mri)

    G = np.zeros((1, X//nx, Y//ny, Z//nz, POINTS), dtype=float)

    for i in range(0, X-nx, nx):
        for j in range(0, Y-ny, ny):
            for k in range(0, Z-nz, nz):

                patch = mri[i:i + nx, j:j + ny, k:k + nz]

                if patch.max():
                    G[0, i // nx, j // ny, k // nz, :] = extract_feature(patch)

    if histName:
        np.save(histName, G)

    # return provides a way to make a larger matrix from different subjects
    return G