import os
from subprocess import check_output

def foregroundMask(directory, prefix, registeredImage):

    mask= os.path.join(directory, prefix+ '-fore-mask.nii.gz')

    try:
        # Command line call:
        # /home/tb571/Downloads/Slicer-4.9.0-2018-08-13-linux-amd64/Slicer --launch ./lib/Slicer-4.9/cli-modules/BRAINSROIAuto -h
        args = ['Slicer', '--launch', 'BRAINSROIAuto',
                '--inputVolume', registeredImage,
                '--outputVolumePixelType', 'uint',
                '--otsuPercentileThreshold', '0.21',
                '--thresholdCorrectionFactor', '0.7',
                '--outputROIMaskVolume', mask
                ]

        check_output(args)

    except:
        print(f"Foreground masking failed of {registeredImage}")
        exit(1)
    
    print(f"Foreground mask created of {registeredImage}")
    return mask