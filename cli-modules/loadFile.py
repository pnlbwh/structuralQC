import nrrd
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import nibabel
    
import distutils.spawn
import pandas as pd
from os.path import isfile

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

    apps = ['antsApplyTransforms',
            'antsRegistrationSyNQuick.sh',
            'antsRegistration',
            'antsRegistrationSyNMI.sh']

    for exe in apps:
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


def loadImageList(file):

    with open(file) as f:

        imgs = []
        content= f.read()
        for line, row in enumerate(content.split()):
            if row and not isfile(row): # handling w/space
                raise FileNotFoundError(f'{row} can\'t be found: check line {line} in {file}')
            else:
                imgs.append(row)


    return imgs