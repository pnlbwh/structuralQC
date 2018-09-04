import os
from subprocess import check_call, call

def registration(directory, prefix, fixedImage, movingImage):

    regImage= os.path.join(directory, prefix+'-reg'+'.nii.gz')

    imgs= f'{fixedImage}, {movingImage}'
    
    try:
        # antsRegistration doesn't work without (' ').join
        args = (' ').join(['antsRegistration', '-d', '3', '-r', f'[{imgs}, 1]',
                '-m', f'mattes[{imgs}, 1, 32, regular, 0.1]',
                '-t', 'affine[0.1]',
                '-c', '[500x500x50, 1e-3, 20]',
                '-s', '4x2x1vox',
                '-n', 'bspline',
                '-f', '3x2x1',
                '-l', '1',
                '-z', '1',
                '-o', f'[{prefix}, {prefix}-reg.nii.gz]'
                ])
              
        # print(args)
        
        # for antsRegistration, shell= True is a must
        check_call(args, shell= True)

        call(['rm', f'{prefix}0GenericAffine.mat'])
        call(['mv', f'{prefix}-reg.nii.gz', directory])
        
    except:
        print("Registration failed")
        exit(1)
    
    print("Registration successful")
    return regImage
    