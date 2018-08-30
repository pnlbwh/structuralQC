import os
from subprocess import check_output

def forgroundMask(directory, prefix, registeredImage):

    mask= os.path.join(directory, prefix+'-fore-mask'+'.nii.gz')

    args = ['./masking.sh', registeredImage, mask]

    try:
        check_output(args)
    except:
        print("Foreground masking failed")
        exit(1)

    # import distutils.spawn
    # foreground_masking_cli = distutils.spawn.find_executable("BRAINSROIAuto")

    return mask