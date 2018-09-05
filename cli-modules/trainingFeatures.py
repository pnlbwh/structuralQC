#!/usr/bin/env python

from plumbum import cli
from feature_represent import feature_represent
from loadFile import loadExternalCommands


class Training(cli.Application):
    """Extracts features from all the images in a directory.
    Registers the images to a reference image, creates foreground
    mask of the reference image, and calculates intensity histogram of
    non zero patches in the registered image. Edit the INPUT section
    of structuralQC/config.ini file before running this application
    """

    register= cli.Flag(
        ['-r', '--registerImage'],
        help= '''Use this option for registering input images to the reference image, 
               specify the reference image.''',
        mandatory= False,
        default= False)

    create= cli.Flag(
        ['-c', '--createMask'],
        help= 'Turn on this flag for creating mask of the registered image',
        mandatory= False,
        default= False)

    hist= cli.Flag(
        ['-f', '--feature'],
        help= 'Turn on this flag for obtaining histogram feature of registered image',
        mandatory= False,
        default= False)

    outDir = cli.SwitchAttr(
        ['-o', '--out'],
        help='''output directory (default: input image directory)
                where feature histograms, registered images, 
                and foreground masks are saved.''',
        mandatory=False)

    def main(self):

        loadExternalCommands()


        if self.register!=None or self.create or self.hist:
            feature_represent(self.register, self.create, self.hist, self.outDir)
        else:
            print('None of the training options has been selected, turn on at least one of the flags.')
            exit(1)

        pass

if __name__ == '__main__':
    Training.run()