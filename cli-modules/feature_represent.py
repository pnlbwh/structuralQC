# TODO: Obtain maskFolder, t1Histogram, t2Histogram, discreteScores from config.ini
# or pass all of them as argument such as
# at least make the user pass the xls file from where discrete scores can be updated as a .txt file
# -r fixedImaget1 has to be passed

import configparser
import os
import numpy as np
import multiprocessing

from loadFile import loadImage, loadCaseList
from slide_filter import slide_filter
from registration import registration
from masking import masking

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

sx = int(config['DEFAULT']['sx'])
sy = int(config['DEFAULT']['sy'])
sz = int(config['DEFAULT']['sz'])

POINTS= int(config['DEFAULT']['POINTS'])

imageFolder= config['INPUT']['imageFolder']
caselist = config['INPUT']['caselist']
subFolder= config['INPUT']['subFolder']
imageSuffix= config['INPUT']['imageSuffix']
modality= config['INPUT']['modality']
fixedImage= config['TRAINING'][f'fixedImage{modality}']


def subject_register(sub_name):
    movingImage= os.path.join(imageFolder, sub_name, subFolder, sub_name + imageSuffix)
    prefix= sub_name+'-'+modality
    registration(outDir, prefix, fixedImage, movingImage)

def subject_mask(sub_name):
    prefix= sub_name+'-'+modality
    registeredImage= os.path.join(outDir, prefix+'-reg')
    masking(maskFolder, prefix , registeredImage)

def subject_histogram(sub_name):
    mri = loadImage(os.path.join(imageFolder, sub_name, subFolder, sub_name + imageSuffix))
    return slide_filter(mri, '')



def feature_represent(register, create, hist, directory):

    global outDir

    # Determine prefix and directory
    if directory == 'None':
        outDir = imageFolder
    else:
        outDir= directory

    subjects= loadCaseList(caselist)
    num_sub= len(subjects)

    if register:
        pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

        res = pool.map_async(subject_register, subjects)
        res.get() # should be necessary to halt program until multiprocessing is complete

        pool.close()
        pool.join()

        print('Completed registration of all the subjects')


    if create:
        global maskFolder
        maskFolder= os.path.join(outDir,'registered_foreground_masks')
        os.makedirs(maskFolder)
        config['TRAINING']['maskFolder']= maskFolder

        pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

        res = pool.map_async(subject_mask, subjects)
        res.get()  # should be necessary to halt program until multiprocessing is complete

        pool.close()
        pool.join()

        print('Completed foreground masking of all the subjects')



    if hist:
        # load one image to get dimension
        mri= loadImage(os.path.join(imageFolder, subjects[0], subFolder, subjects[0]+imageSuffix))
        X, Y, Z= np.shape(mri)

        H = np.zeros((num_sub, X//(nx*sx), Y//(ny*sy), Z//(nz*sz), POINTS), dtype=float)

        pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

        res = pool.map_async(subject_histogram, subjects)
        value = res.get()
        for i in range(num_sub):
            H[i,: ] = value[i]

        pool.close()
        pool.join()

        histName= os.path.join(outDir, f'patch_histograms_{modality}.npy')
        if modality=='t1':
            config['TRAINING']['t1Histogram'] = histName
        else:
            config['TRAINING']['t2Histogram'] = histName

        np.save(histName, H)

        print('Completed histogram extraction of all the subjects')