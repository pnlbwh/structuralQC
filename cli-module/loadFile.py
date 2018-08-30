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


