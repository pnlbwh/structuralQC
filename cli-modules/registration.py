import os
from subprocess import check_call
from plumbum.cmd import antsApplyTransforms
from plumbum import FG


def registration(directory, prefix, fixedImage, fixedMask, movingImage, threads=4):

    outPrefix= os.path.join(directory, prefix)

    try:
        if not fixedMask:
            check_call((' ').join(['antsRegistrationSyNMI.sh',
                                   '-d', '3',
                                   '-f', fixedImage,
                                   '-m', movingImage,
                                   '-o', outPrefix,
                                   '-n', str(threads),
                                   ]), shell = True)
        else:
            check_call((' ').join(['antsRegistrationSyNMI.sh',
                                   '-d', '3',
                                   '-f', fixedImage,
                                   '-x', fixedMask,
                                   '-m', movingImage,
                                   '-o', outPrefix,
                                   '-n', str(threads),
                                   ]), shell = True)

        warp = outPrefix + '1Warp.nii.gz'
        trans = outPrefix + '0GenericAffine.mat'
        regImage = os.path.join(directory, prefix + '-reg.nii.gz')

        antsApplyTransforms[
            '-d', '3',
            '-i', movingImage,
            '-o', regImage,
            '-r', fixedImage,
            '-t', warp, trans
        ] & FG

        check_call(['rm', warp])
        check_call(['rm', trans])
        check_call(['rm', outPrefix + 'Warped.nii.gz'])
        check_call(['rm', outPrefix + '1InverseWarp.nii.gz'])
        check_call(['rm', outPrefix + 'InverseWarped.nii.gz'])

        print(f"Registration successful of {os.path.basename(movingImage)}")
        return regImage


    except:
        raise RuntimeError(f"Registration failed of {os.path.basename(movingImage)}")