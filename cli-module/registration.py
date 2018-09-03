import os
from subprocess import check_output, call

def registration(directory, prefix, fixedImage, movingImage):

    # import distutils.spawn
    # registration_cli = distutils.spawn.find_executable("antsRegistration")
    reg= os.path.join(directory, prefix+'-reg'+'.nii.gz')

    imgs= fixedImage,movingImage

    try:
        args = ['antsRegistration', '-d' '3', '-r' f'[{imgs}, 1]',
                '-m', f'mattes[{imgs}, 1, 32, regular, 0.1]',
                '-t', 'affine[0.1]',
                '-c', '[500x500x50, 1e-3, 20]',
                '-s', '4x2x1vox',
                '-n', 'bspline',
                '-f', '3x2x1',
                '-l', '1',
                '-z', '1',
                '-o', f'[{prefix}, {prefix}-reg.nii.gz]'
                ]
        check_output(args)

        call(['rm', f'{prefix}0GenericAffine.mat'])
        call(['mv', f'${prefix}-reg.nii.gz', directory])

    except:
        print("Registration failed")
        exit(1)

    return reg