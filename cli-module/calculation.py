import configparser
import numpy as np
from scipy.stats import pearsonr
import glob

import os, sys

from registration import registration
from masking import foregroundMask
from extract_feature import extract_feature
from loadFile import loadFile, loadExcel, loadExecutable
from slide_filter import slide_filter

# global configurations ---------------------------------------
# get structuralQC directory
moduleDir= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
eps = 2.2204e-16 # a small number to prevent divide by zero

config = configparser.ConfigParser()
config.read(os.path.join(moduleDir,'structuralQC','config.ini'))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

sx = int(config['DEFAULT']['sx'])
sy = int(config['DEFAULT']['sy'])
sz = int(config['DEFAULT']['sz'])

decisionFactor= int(config['DEFAULT']['decisionFactor'])

eta = float(config['DEFAULT']['eta'])
metric= config['DEFAULT']['metric']

discreteScores = [int(x) for x in config['TRAINING']['discreteScores'].split(',')]
fixedImaget1= os.path.join(moduleDir, config['TRAINING']['fixedImaget1'])
fixedImaget2= os.path.join(moduleDir, config['TRAINING']['fixedImaget2'])

# ----------------------------------------------------------------

def BC(P, Q):
    return -np.log(np.sum([np.sqrt(P[i]*Q[i]) for i in range(len(P))]))

def KL(P, Q):
    P += eps
    Q += eps
    return np.sum([P[i]*np.log(P[i]/Q[i]) for i in range(len(P))])


def processImage(imgPath, maskPath, directory, modality):
    
    apps = ['Slicer', 'antsRegistration', 'BRAINSROIAuto']
    for exe in apps:
        os.environ["PATH"]+= ':'+os.path.abspath(config['EXECUTABLES'][exe])
        loadExecutable(exe)
    
    print('All executables are found, program will begin now ...')

    # for debugging
    print(imgPath)

    # Determine prefix and directory
    if directory == 'None':
        directory = os.path.dirname(os.path.abspath(imgPath))

    prefix = os.path.basename(imgPath).split('.')[0]

    # check if 'reg' keyword exists in prefix, if not then register to fixedImage
    if 'reg' not in prefix:
        print('\'reg\' keyword is not present in input image. Registering with reference image ...')
        
        if modality=='t1':
            regPath = registration(directory, prefix, fixedImaget1, imgPath)
        else:
            regPath = registration(directory, prefix, fixedImaget2, imgPath)
    else:
        regPath= imgPath
        print('Registered image found ...');


    # if mask not provided, check for 'fore-mask' keyword in input directory, if not then create foreground mask
    if maskPath=='None':

        potentialMask= glob.glob(os.path.join(directory, '*fore-mask*'))
        num= len(potentialMask)
        if num>1:
            print('Multiple foreground mask exists in input image directory (default).'
                  'Delete all but one and try again')
            exit(1)

        elif num==0:
            print('Creating mask ...')
            # create the foreground mask
            maskPath= foregroundMask(directory, prefix, imgPath)
        
        else:
            maskPath= potentialMask[0]
            print('Mask found ...')


    # load the mri and the mask
    mri= loadFile(regPath)
    mask= loadFile(maskPath)

    # extract feature from the mri
    histName = os.path.join(directory, prefix + '-histogram' + '.npy')
    H_test= slide_filter(mri, histName)

    dim= np.shape(mri)

    fid= open(os.path.join(directory, prefix + '-quality' + '.txt'), 'w')
    predictQuality(dim, H_test, mask, modality, fid)


def predictQuality(dim, H1, m1, modality, fid):

    excelFile= os.path.join(moduleDir, config['TRAINING']['visual_qc_excel_file'])
    subjects, ratings= loadExcel(excelFile, modality)
    subjects= [str(i) for i in subjects]
    
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

            m2= loadFile(os.path.join(maskFolder, subjects[m], subjects[m] + maskSuffix)) # reference mask

            for i in range(0, X, sx*nx):
                for j in range(0, Y, sy*ny):
                    for k in range(0, Z, sz*nz):

                        p1 = m1[i:i + nx, j:j + ny, k:k + nz] # Test patch
                        p2 = m2[i:i + nx, j:j + ny, k:k + nz] # Reference patch

                        P = H1[0, i // (nx*sx), j // (ny*sy), k // (nz*sz), :] # Test histogram
                        Q = H2[m, i // (nx*sx), j // (ny*sy), k // (nz*sz), :] # Reference histogram

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

    predicted_score= np.argmax(class_score)

    # for debugging
    print(predicted_score)

    fid.write(f'Predicted score: {predicted_score} ({min(discreteScores)} being worst, {max(discreteScores)} being best) \n')
    fid.write('Decision: {}'.format('pass' if predicted_score>max(discreteScores)/decisionFactor else 'fail'))
    fid.close()

    return predicted_score

