import nrrd
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import nibabel
    
import distutils.spawn
import pandas as pd

import os, configparser

def loadNrrd(fileName):
    img = nrrd.read(fileName)
    return img[0]

def loadNifti(fileName):
    img = nibabel.load(fileName)
    return img.get_data()

def loadImage(filePath):

    if filePath.endswith('.nii') or filePath.endswith('.nii.gz'):
        img= loadNifti(filePath)
    elif filePath.endswith('.nrrd') or ('.nhdr'):
        img= loadNrrd(filePath)

    else:
        print('Invalid file format, accepted formats: nii, nii.gz, nrrd, and nhdr')
        exit(1)

    return img
    
def loadExcel(fileName, modality):

    df = pd.read_excel(fileName)
    subjects= df["Subject ID"].values
    ratings= df[modality+" score"].values
    subjects= [str(i) for i in subjects]
    
    return (subjects, ratings)
    
    
def loadExecutable(exe):

    if distutils.spawn.find_executable(exe) is None:
        print(f'{exe} could not be found')
        print(f'Set {exe} path in config.ini and retry')
        exit(1)
    else:
        print(f'{exe} found')


def loadExternalCommands():

    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))

    apps = ['Slicer', 'antsRegistration', 'BRAINSROIAuto']
    for exe in apps:
        os.environ["PATH"] += ':' + os.path.abspath(config['EXECUTABLES'][exe])
        loadExecutable(exe)

    print('All executables are found, program will begin now ...')


def loadCaseList(fileName):

    f= open(fileName, 'r')

    # omit any empty line in the caselist.txt
    subjects= [ ]
    for s in list(f):
        temp= s.strip()
        if temp:
            subjects.append(temp)


    return subjects