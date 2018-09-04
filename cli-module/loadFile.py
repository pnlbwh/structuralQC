import nrrd
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import nibabel
    
import distutils.spawn
import pandas as pd
import sys

def loadNrrd(fileName):
    img = nrrd.read(fileName)
    return img[0]

def loadNifti(fileName):
    img = nibabel.load(fileName)
    return img.get_data()

def loadFile(filePath):

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

    return (subjects, ratings)
    
    
def loadExecutable(exe):

    if distutils.spawn.find_executable(exe) is None:
        print(f'{exe} could not be found')
        print(f'Set {exe} path in config.ini and retry')
        exit(1)
    else:
        print(f'{exe} found')        