import configparser
import numpy as np
from scipy.stats import pearsonr
import glob
from registration import registration
from masking import masking
import os
import pandas as pd

# global configurations ---------------------------------------
# get structuralQC directory
moduleDir= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
eps = 2.2204e-16 # a small number to prevent divide by zero

config = configparser.ConfigParser()
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

sx = int(config['DEFAULT']['sx'])
sy = int(config['DEFAULT']['sy'])
sz = int(config['DEFAULT']['sz'])

decisionFactor= int(config['DEFAULT']['decisionFactor'])

eta = float(config['DEFAULT']['eta'])
POINTS= int(config['DEFAULT']['POINTS'])
metric= config['DEFAULT']['metric']

discreteScores = [int(x) for x in config['TRAINING']['discreteScores'].split(',')]
fixedImaget1= config['TRAINING']['fixedImaget1']
fixedImaget2= config['TRAINING']['fixedImaget2']

# ----------------------------------------------------------------

import nrrd
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import nibabel

def loadNrrd(fileName):
    img = nrrd.read(fileName)
    return img[0]

def loadNifti(fileName):
    img = nibabel.load(fileName)
    return img.get_data()

def loadFiles(filePath):

    if filePath.endswith('.nii') or filePath.endswith('.nii.gz'):
        img= loadNrrd(filePath)
    elif filePath.endswith('.nrrd') or ('.nhdr'):
        img= loadNifti(filePath)

    else:
        print('Invalid file format, accepted formats: nii, nii.gz, nrrd, and nhdr')
        exit(1)

    return img


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


def slide_filter(mri, histName):

    X, Y, Z = np.shape(mri)

    G = np.zeros((1, X//(nx*sx), Y//(ny*sy), Z//(nz*sz), POINTS), dtype=float)


    for i in range(0, X, nx*sx):
        for j in range(0, Y, ny*sy):
            for k in range(0, Z, nz*sz):

                patch = mri[i:i + nx, j:j + ny, k:k + nz]

                if patch.max():
                    G[0, i // nx, j // ny, k // nz, :] = extract_feature(patch)

    if histName:
        np.save(histName, G)

    # return provides a way to make a larger matrix from different subjects
    return G


def BC(P, Q):
    return -np.log(np.sum([np.sqrt(P[i]*Q[i]) for i in range(len(P))]))

def KL(P, Q):
    P += eps
    Q += eps
    return np.sum([P[i]*np.log(P[i]/Q[i]) for i in range(len(P))])


def loadExcel(fileName, modality):

    df = pd.read_excel(fileName)
    subjects= df["Subject ID"].values
    ratings= df[modality+" score"].values

    return (subjects, ratings)



def processImage(imgPath, maskPath, directory, modality):

    # for debugging
    print(imgPath)

    # Determine prefix and directory
    if directory == 'None':
        directory = os.path.dirname(os.path.abspath(imgPath))

    prefix = os.path.basename(imgPath).split('.')[0]

    # check if 'reg' keyword exists in prefix, if not then register to fixedImage
    if 'reg' not in prefix:
        if modality=='t1':
            regPath = registration(directory, prefix, fixedImaget1, imgPath)
        else:
            regPath = registration(directory, prefix, fixedImaget2, imgPath)
    else:
        regPath= imgPath


    # if mask not provided, check for 'fore-mask' keyword in input directory, if not then create foreground mask
    if maskPath=='None':

        potentialMasks= len(glob.glob(directory, '*fore-mask*'))
        if potentialMasks>1:
            print('Multiple foreground mask exists. Delete all but one and try again')
            exit(1)

        elif potentialMasks==0:
            # create the foreground mask
            maskPath= masking(directory, prefix, imgPath)


    # load the mri and the mask
    mri= loadFiles(regPath)
    mask= loadFiles(maskPath)

    # extract feature from the mri
    histName = os.path.join(directory, prefix + '-histogram' + '.npy')
    H_test= slide_filter(mri, histName)

    dim= mri.shape()

    fid= open(os.path.join(directory, prefix + '-quality' + '.txt'), 'w')
    predictQuality(dim, H_test, mask, modality, fid)


def predictQuality(dim, H1, m1, modality, fid):

    excelFile= os.path.join(moduleDir, config['TRAINING']['visual_qc_excel_file'])
    subjects, ratings= loadExcel(excelFile, modality)

    # load reference histogram file
    H2= np.load(os.path.join(moduleDir, config['TRAINING'][modality+'Histogram']))

    maskFolder= os.path.join(moduleDir, config['TRAINING']['maskFolder'])
    maskSuffix= config['TRAINING'][f'{modality}MaskSuffix']


    class_score= np.zeros(len(discreteScores), dtype= float)

    X, Y, Z= dim
    for s in discreteScores:

        ind= np.where(ratings==s)[0]
        temp = np.zeros(int((len(ind) * X / nx * Y / ny * Z / nz)/(sx*sy*sz)), dtype=float)
        counter= 0

        for m in ind: # reference subjects

            m2= loadFiles(os.path.join(maskFolder, subjects[m]+ maskSuffix)) # reference mask

            for i in range(0, X, sx*nx):
                for j in range(0, Y, sy*ny):
                    for k in range(0, Z, sz*nz):

                        p1 = m1[i:i + nx, j:j + ny, k:k + nz] # Test patch
                        p2 = m2[i:i + nx, j:j + ny, k:k + nz] # Reference patch

                        P = H1[0, i // nx, j // ny, k // nz, :] # Test histogram
                        Q = H2[m, i // nx, j // ny, k // nz, :] # Reference histogram

                        if p1.max() and p2.max() and np.multiply(P,Q).sum() and np.multiply(p1, p2).sum()> 0.5*eta*(p1.sum()+p2.sum()):

                            if metric == 'PEARSON':
                                temp[counter]= max(pearsonr(P, Q))

                            elif metric == 'BC':
                                temp[counter]= BC(P, Q)

                            elif metric == 'KL':
                                temp[counter]= KL(P, Q)

                            elif metric == 'MSE':
                                temp[counter]= ((P-Q)**2).sum()


                            counter+=1


        class_score[s-1]= temp.sum()/counter

    predicted_score= max(class_score)

    # for debugging
    print(predicted_score)

    fid.write(f'Predicted score: {predicted_score} ({min(discreteScores)} being worst, {max(discreteScores)} being best) \n')
    fid.write('Decision: {}'.format('pass' if predicted_score>max(discreteScores)/decisionFactor else 'fail'))
    fid.close()

    return predicted_score





