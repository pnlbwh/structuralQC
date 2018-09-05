# !/usr/bin/env python

from plumbum import cli
from feature_represent import feature_represent
from loadFile import loadExternalCommands
import os, configparser


class Training(cli.Application):
    """Extracts features from all the images in a directory.
    Registers the images to a reference image, creates foreground mask
    of the reference image, and calculates intensity histogram
    of non zero patches in the registered image.
    """

    register= cli.Flag(
        ['-r', '--registerImage'],
        help= 'Turn on this flag for registering input images to the reference image',
        mandatory= False,
        default= False)

    create= cli.Flag(
        ['-c', '--createMask'],
        help= 'Turn on this flag for creating mask of the registered image',
        mandatory= False,
        default= False)

    hist= cli.Flag(
        ['-h', '--hist'],
        help= 'Turn on this flag for obtaining histogram of registered image',
        mandatory= False,
        default= False)

    outDir = cli.SwitchAttr(
        ['-o', '--out'],
        help='''output directory (default: input image directory)
                where feature histograms, registered images, 
                and foreground masks are saved.
                ''',
        mandatory=False)

    def main(self):

        self.modality = self.modality.lower()

        if self.modality != 't1' and self.modality != 't2':
            print('Invalid structural mri, valid types: t1/t2')
            exit(1)

        loadExternalCommands()
        
        if self.register or self.create or self.hist:
            feature_represent(self.register, self.create, self.hist, self.outDir)
        else:
            print('None of the training options has been selected, turn on at least one of the flags.')
            exit(1)
            

if __name__ == '__main__':
    Training.run()