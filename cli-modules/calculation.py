import configparser
import numpy as np
from scipy.stats import pearsonr
import os

from registration import registration
from loadFile import loadImage, loadExcel
from slide_filter import slide_filter

SCRIPTDIR= os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(SCRIPTDIR, 'config.ini'))

# global configurations ---------------------------------------
eps = 2.2204e-16 # a small number to prevent divide by zero
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

sx = int(config['DEFAULT']['sx'])
sy = int(config['DEFAULT']['sy'])
sz = int(config['DEFAULT']['sz'])

decisionFactor= int(config['DEFAULT']['decisionFactor'])

eta = float(config['DEFAULT']['eta'])
metric= config['DEFAULT']['metric']

discreteScores = [int(x) for x in config['TRAINING']['discreteScores'][1:-1].split(',')]
fixedImaget1= config['TRAINING']['fixedImaget1']
fixedImaget2= config['TRAINING']['fixedImaget2']
fixedMaskt1= config['TRAINING']['fixedMaskt1']
fixedMaskt2= config['TRAINING']['fixedMaskt2']
excelFile= config['TRAINING']['visual_qc_excel_file']
# if not fixedMaskt1:
#     fixedMaskt1 = None
# if not fixedMaskt2:
#     fixedMaskt2 = None

# ----------------------------------------------------------------

def BC(P, Q):
    return -np.log(np.sum([np.sqrt(P[i]*Q[i]) for i in range(len(P))]))

def KL(P, Q):
    P += eps
    Q += eps
    return np.sum([P[i]*np.log(P[i]/Q[i]) for i in range(len(P))])


def processImage(imgPath, directory, modality):

    # for debugging
    print(imgPath)

    # Determine prefix and directory
    if not directory:
        directory = os.path.dirname(os.path.abspath(imgPath))
    elif not os.path.exists(directory):
        os.makedirs(directory)

    prefix = os.path.basename(imgPath).split('.')[0]

    # check if 'reg' keyword exists in prefix, if not then register to fixedImage
    if 'reg' not in prefix:
        print('\'reg\' keyword is not present in input image. Registering with reference image ...')

        if modality=='t1':
            regPath = registration(directory, prefix, fixedImaget1, fixedImaget1, imgPath)
        else:
            regPath = registration(directory, prefix, fixedImaget2, fixedImaget2, imgPath)
    else:
        regPath= imgPath
        print('Registered image found ...')

    # load the mri and the mask
    mri= loadImage(regPath)

    # extract feature from the mri
    # histName = os.path.join(directory, prefix + '-histogram' + '.npy')
    # H_test= slide_filter(mri*mask, histName)
    H_test= slide_filter(mri, '')

    dim= np.shape(mri)

    fid= open(os.path.join(directory, prefix + '-quality' + '.txt'), 'w')

    print("Checking quality ...")
    prediction= predictQuality(dim, H_test, modality, fid)

    return prediction

def predictQuality(dim, H1, modality, fid):

    subjects, ratings= loadExcel(excelFile, modality)

    # load reference histogram file
    H2= np.load(config['TRAINING'][modality+'Histogram'])

    class_score= np.zeros(len(discreteScores), dtype= float)

    X, Y, Z= dim
    for l, s in enumerate(discreteScores):

        ind= np.where(ratings==s)[0]
        temp = np.zeros(int((len(ind) * X / nx * Y / ny * Z / nz)/(sx*sy*sz)), dtype=float)
        counter= 0

        for m in ind: # reference subjects

            for i in range(0, X-nx, sx*nx):
                for j in range(0, Y-nx, sy*ny):
                    for k in range(0, Z-nx, sz*nz):

                        P = H1[0, i // nx, j // ny, k // nz, :] # Test histogram
                        Q = H2[m, i // nx, j // ny, k // nz, :] # Reference histogram

                        if np.multiply(P,Q).sum():

                            if metric == 'PEARSON':
                                temp[counter]= max(pearsonr(P, Q))

                            elif metric == 'BC':
                                temp[counter]= BC(P, Q)

                            elif metric == 'KL':
                                temp[counter]= KL(P, Q)

                            elif metric == 'MSE':
                                temp[counter]= ((P-Q)**2).sum()


                            counter+=1


        class_score[l]= temp.sum()/counter

    if metric == 'PEARSON':
        predicted_score= discreteScores[np.argmax(class_score)]
    else:
        predicted_score= discreteScores[np.argmin(class_score)]

    score_range= np.ptp(discreteScores)+1 if min(discreteScores)>0 else np.ptp(discreteScores)
    quality= 'pass' if predicted_score>score_range/decisionFactor else 'fail'
    # for debugging
    print(predicted_score, quality)

    fid.write(f'Predicted score: {predicted_score} ({min(discreteScores)} being worst, {max(discreteScores)} being best) \n')
    fid.write(f'Decision: {quality} \n')
    fid.close()

    return (predicted_score, quality)

def main():
    pass
    # test the algorithm on a test image
    # processImage()

if __name__== '__main__':
    main()