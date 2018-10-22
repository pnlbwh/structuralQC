import configparser
import os
import numpy as np
import multiprocessing
import time

from loadFile import loadImage, loadCaseList, loadExcel
from slide_filter import slide_filter
from registration import registration
from masking import foregroundMask
from errorChecking import errorChecking, EXIT
import glob
from subprocess import call

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
nx = int(config['DEFAULT']['nx'])
ny = int(config['DEFAULT']['ny'])
nz = int(config['DEFAULT']['nz'])

POINTS= int(config['DEFAULT']['POINTS'])

'''
config_input = configparser.ConfigParser()
config_input.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config_input.ini')))
imageFolder= config_input['INPUT']['imageFolder']
caselist = config_input['INPUT']['caselist']
subFolder= config_input['INPUT']['subFolder']
imageSuffix= config_input['INPUT']['imageSuffix']
modality= config_input['INPUT']['modality']
excelFile= config_input['INPUT']['visual_qc_excel_file']
'''

def subject_register(sub_name):
    print('Registering subject ', sub_name)

    #movingImage= os.path.join(imageFolder, sub_name, subFolder, sub_name + imageSuffix)

    # inside imageFolder, images are grouped by subject folders
    # imageSuffix should be "*t1*nii.gz" or "*t1*-reg.nii.gz" based on unregistered or registered image
    temp= glob.glob(os.path.join(imageFolder, sub_name, subFolder, sub_name+imageSuffix))
    if len(temp)>1:
        EXIT(f"Multiple {modality} images found with the provided suffix, make that unique, and try again.")
    movingImage= temp[0]

    prefix= sub_name+'-'+modality
    directory= os.path.join(imageFolder, sub_name, subFolder)
    registration(directory, prefix, fixedImage, movingImage)
    # registration(outDir, prefix, fixedImage, movingImage)


def subject_mask(sub_name):
    print('Creating mask of subject ', sub_name)
    prefix= sub_name+'-'+modality
    directory = os.path.join(imageFolder, sub_name, subFolder)
    registeredImage = os.path.join(imageFolder, sub_name, subFolder, prefix + '-reg.nii.gz')
    # registeredImage= os.path.join(outDir, prefix+'-reg.nii.gz')
    foregroundMask(directory, prefix, registeredImage)
    # in training mode, copy the masks to maskFolder

def subject_histogram(sub_name):
    print('Calculating histogram of subject ', sub_name)

    # the following image is always a registered image
    temp = glob.glob(os.path.join(imageFolder, sub_name, subFolder, sub_name + imageSuffix))
    if len(temp)>1:
        EXIT(f"Multiple {modality} images found with the provided suffix, make that unique, and try again.")

    mri = loadImage(temp[0])
    try:
        H= slide_filter(mri, '')
        print(f'Histogram calculation successful of subject {sub_name}')
        return H
    except:
        print(f'Histogram calculation failed of subject {sub_name}')
        exit(1)



def feature_represent(imgDir, subDir, type, suffix,
                      caselist, excelFile, register, create, hist, directory, trainMode):

    global imageFolder, subFolder, imageSuffix, modality, outDir

    imageFolder = imgDir
    subFolder = subDir
    imageSuffix = suffix
    modality = type

    # Determine prefix and directory
    # the output directory is where masks and histograms are stored
    if not directory:
        directory = imageFolder
    elif not os.path.exists(directory):
        os.makedirs(directory)

    outDir= directory

    if not subFolder:
        subFolder= '.'

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

        # now the imageSuffix should point to registered images
        imageSuffix= f'-{modality}-reg.nii.gz'


    if create:

        t1= time.time()

        global maskFolder
        maskFolder= os.path.join(outDir,'registered_foreground_masks')
        if not os.path.exists(maskFolder):
            os.makedirs(maskFolder)
        config['TRAINING']['maskFolder']= maskFolder
        config['TRAINING'][f'{modality}MaskSuffix']= f'-{modality}-fore-mask.nii.gz'

        pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

        res = pool.map_async(subject_mask, subjects)
        res.get()  # should be necessary to halt program until multiprocessing is complete

        pool.close()
        pool.join()

        print('Completed foreground masking of all the subjects')
        print(f'Time taken in mask creation {time.time()-t1} seconds')

        if trainMode:
            for sub in subjects:
                call(['cp', os.path.join(imageFolder, sub, subFolder, f'{sub}-{modality}-fore-mask.nii.gz'), maskFolder])


    if hist:

        t1= time.time()

        # load one image to get dimension
        # mri= loadImage(os.path.join(imageFolder, subjects[0], subFolder, subjects[0]+imageSuffix))
        mri= loadImage(config['TRAINING'][f'fixedImage{modality}'])
        X, Y, Z= np.shape(mri)

        H = np.zeros((num_sub, X//nx, Y//ny, Z//nz, POINTS), dtype=float)

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