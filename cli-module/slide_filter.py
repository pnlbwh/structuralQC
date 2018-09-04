import numpy as np
import configparser
from extract_feature import extract_feature
import os

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

sx = int(config['DEFAULT']['sx'])
sy = int(config['DEFAULT']['sy'])
sz = int(config['DEFAULT']['sz'])

POINTS= int(config['DEFAULT']['POINTS'])

def slide_filter(mri, histName):

    X, Y, Z = np.shape(mri)

    G = np.zeros((1, X//(nx*sx), Y//(ny*sy), Z//(nz*sz), POINTS), dtype=float)


    for i in range(0, X, nx*sx):
        for j in range(0, Y, ny*sy):
            for k in range(0, Z, nz*sz):

                patch = mri[i:i + nx, j:j + ny, k:k + nz]

                if patch.max():
                    G[0, i // (nx*sx), j // (ny*sy), k // (nz*sz), :] = extract_feature(patch)

    if histName:
        np.save(histName, G)

    # return provides a way to make a larger matrix from different subjects
    return G