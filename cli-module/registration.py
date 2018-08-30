import os
from subprocess import check_output

def registration(directory, prefix, fixedImage, movingImage):

    # import distutils.spawn
    # registration_cli = distutils.spawn.find_executable("antsRegistration")
    reg= os.path.join(directory, prefix+'-reg'+'.nii.gz')

    imgs= [fixedImage,movingImage]
    op=prefix

    args = ['./registration.sh', imgs, op, directory]

    try:
        check_output(args)
    except:
        print("Registration failed")
        exit(1)

    return reg