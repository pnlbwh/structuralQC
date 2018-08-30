import numpy as np
import configparser
from extract_feature import extract_feature

def slide_filter(mri):

    config = configparser.ConfigParser()
    nx = config['DEFAULT']['nx']
    ny = config['DEFAULT']['ny']
    nz = config['DEFAULT']['nz']

    sx = config['DEFAULT']['sx']
    sy = config['DEFAULT']['sy']
    sz = config['DEFAULT']['sz']

    POINTS= config['DEFAULT']['POINTS']

    X, Y, Z = np.shape(mri)

    G = np.zeros((1, X//(nx*sx), Y//(ny*sy), Z//(nz*sz), POINTS), dtype=float)


    for i in range(0, X, nx*sx):
        for j in range(0, Y, ny*sy):
            for k in range(0, Z, nz*sz):

                patch = mri[i:i + nx, j:j + ny, k:k + nz]

                if patch.max():
                    G[0, i // nx, j // ny, k // nz, :] = extract_feature(patch)


    return G