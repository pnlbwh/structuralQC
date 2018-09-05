import configparser
import os
import numpy as np
import multiprocessing
import time

from loadFile import loadImage, loadCaseList, loadExcel
from slide_filter import slide_filter
from registration import registration
from masking import foregroundMask
from errorChecking import errorChecking

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

sx = int(config['DEFAULT']['sx'])
sy = int(config['DEFAULT']['sy'])
sz = int(config['DEFAULT']['sz'])

POINTS= int(config['DEFAULT']['POINTS'])

config_input = configparser.ConfigParser()
config_input.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config_input.ini')))
imageFolder= config_input['INPUT']['imageFolder']
caselist = config_input['INPUT']['caselist']
subFolder= config_input['INPUT']['subFolder']
imageSuffix= config_input['INPUT']['imageSuffix']
modality= config_input['INPUT']['modality']
excelFile= config_input['INPUT']['visual_qc_excel_file']


def subject_register(sub_name):
    print('Registering subject ', sub_name)
    movingImage= os.path.join(imageFolder, sub_name, subFolder, sub_name + imageSuffix)
    prefix= sub_name+'-'+modality
    registration(outDir, prefix, fixedImage, movingImage)

def subject_mask(sub_name):
    print('Creating mask of subject ', sub_name)
    prefix= sub_name+'-'+modality
    registeredImage= os.path.join(outDir, prefix+'-reg')
    foregroundMask(maskFolder, prefix , registeredImage)

def subject_histogram(sub_name):
    print('Calculating histogram of subject ', sub_name)
    mri = loadImage(os.path.join(imageFolder, sub_name, subFolder, sub_name + imageSuffix))
    return slide_filter(mri, '')



def feature_represent(register, create, hist, directory):


    global outDir

    # Determine prefix and directory
    if not directory:
        outDir = imageFolder
    elif not os.path.exists(directory):
        os.makedirs(directory)
        outDir= directory

    subjects= loadCaseList(caselist)
    num_sub= len(subjects)

    # read the Subject ID and {modality} column
    cases, visual_scores= loadExcel(excelFile, modality)

    errorChecking(subjects, cases)

    config['TRAINING']['discreteScores']= str(list(set(visual_scores)))
    config['TRAINING']['visual_qc_excel_file']= excelFile


    if register:

        t1= time.time()

        global fixedImage
        fixedImage= register
        config['TRAINING'][f'fixedImage{modality}']= fixedImage

        pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

        res = pool.map_async(subject_register, subjects)
        res.get() # should be necessary to halt program until multiprocessing is complete

        pool.close()
        pool.join()

        print('Completed registration of all the subjects')
        print(f'Time taken in registration {time.time()-t1} seconds')


    if create:

        t1= time.time()

        global maskFolder
        maskFolder= os.path.join(outDir,'registered_foreground_masks')
        os.makedirs(maskFolder)
        config['TRAINING']['maskFolder']= maskFolder
        config['TRAINING'][f'{modality}MaskSuffix']= f'-{modality}-reg-fore-mask.nii.gz'

        pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

        res = pool.map_async(subject_mask, subjects)
        res.get()  # should be necessary to halt program until multiprocessing is complete

        pool.close()
        pool.join()

        print('Completed foreground masking of all the subjects')
        print(f'Time taken in mask creation {time.time()-t1} seconds')



    if hist:

        t1= time.time()

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

        print('Completed histogram calculation of all the subjects.')
        print(f'Time taken in histogram calculation {time.time()-t1} seconds')

    # write back the config.ini after everything
    with open(os.path.join(os.path.dirname(__file__), '..', 'config.ini'),'w') as f:
        config.write(f)