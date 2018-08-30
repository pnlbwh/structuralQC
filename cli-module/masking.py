import os
from subprocess import check_output

def forgroundMask(directory, prefix, registeredImage):

    # import distutils.spawn
    # foreground_masking_cli = distutils.spawn.find_executable("BRAINSROIAuto")
    mask= os.path.join(directory, prefix+'-fore-mask'+'.nii.gz')

    try:
        args = ['BRAINSROIAuto'
                '--inputVolume', registeredImage,
                '--outputVolumePixelType', 'uint',
                '--otsuPercentileThreshold', '0.21',
                '--thresholdCorrectionFactor', '0.7',
                '--outputROIMaskVolume', mask
                ]

        check_output(args)

    except:
        print("Foreground masking failed")
        exit(1)

    return mask