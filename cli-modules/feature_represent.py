import configparser
import numpy as np
import multiprocessing
import time

from loadFile import loadImage, loadCaseList, loadExcel
from slide_filter import slide_filter
from registration import registration
from errorChecking import errorChecking, globCheck

from os.path import abspath, dirname, basename, join as pjoin

SCRIPTDIR= abspath(dirname(__file__))
config = configparser.ConfigParser()
config.read(pjoin(SCRIPTDIR, 'config.ini'))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

POINTS= int(config['DEFAULT']['POINTS'])
excelFile= config['TRAINING']['visual_qc_excel_file']
N_CPU= int(config['RESOURCE']['N_CPU'])

def subject_histogram(filepath):

    subBaseName= basename(filepath)
    print('Calculating histogram of', subBaseName)

    mri = loadImage(filepath)

    H = slide_filter(mri, '')
    print('Histogram calculation successful of', subBaseName)

    return H


def feature_represent(imgs, subjects, register, hist, modality, outDir):

    num_sub= len(subjects)

    # read the Subject ID and {modality} column
    cases, visual_scores= loadExcel(excelFile, modality)

    errorChecking(subjects, cases)

    config['TRAINING']['discreteScores']= str(list(set(visual_scores)))
    config['TRAINING']['visual_qc_excel_file']= excelFile


    regImgs= imgs
    if register:

        t1= time.time()

        fixedImage= config['TRAINING'][f'fixedImage{modality}']
        fixedMask = config['TRAINING'][f'fixedMask{modality}']

        # Use all available cores, otherwise specify the number you want as an argument
        pool = multiprocessing.Pool(N_CPU)
        res=[]
        for movingImage in imgs:
            directory= dirname(movingImage)
            prefix= basename(movingImage).split('.')[0]

            res.append(pool.apply_async(func= registration, args= (directory, prefix, fixedImage, fixedMask, movingImage)))

        regImgs=[]
        for r in res:
            regImgs.append(r.get())

        pool.close()
        pool.join()

        print('Completed registration of all the subjects')
        print(f'Time taken in registration {time.time()-t1} seconds')


    # if registration is done, we must obtain histogram again
    if register or hist:

        t1= time.time()

        # load one image to get dimension
        mri= loadImage(config['TRAINING'][f'fixedImage{modality}'])
        X, Y, Z= np.shape(mri)

        H = np.zeros((num_sub, X//nx, Y//ny, Z//nz, POINTS), dtype=float)

        # Use all available cores, otherwise specify the number you want as an argument
        pool = multiprocessing.Pool(N_CPU)

        res = pool.map_async(subject_histogram, regImgs)
        value = res.get()
        for i in range(num_sub):
            H[i,: ] = value[i]

        pool.close()
        pool.join()

        histName= pjoin(outDir, f'patch_histograms_{modality}.npy')
        if modality=='t1':
            config['TRAINING']['t1Histogram'] = histName
        else:
            config['TRAINING']['t2Histogram'] = histName

        np.save(histName, H)

        print('Completed histogram calculation of all the subjects.')
        print(f'Time taken in histogram calculation {time.time()-t1} seconds')


    # write back the config.ini after everything
    with open(pjoin(dirname(__file__), '..', 'config.ini'),'w') as f:
        config.write(f)