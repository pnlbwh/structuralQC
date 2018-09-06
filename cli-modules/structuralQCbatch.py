#!/usr/bin/env python

from plumbum import cli
from batchProcessing import batchProcessing
from loadFile import loadExecutable, loadExternalCommands
from feature_represent import feature_represent
from errorChecking import EXIT
import time


class batchQC(cli.Application):
    """Checks the quality of all structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    """

    imgDir = cli.SwitchAttr(
        ['-i', '--inputDir'],
        cli.ExistingDirectory,
        help='''structural image folder
                inside image folder, there should be other folders 
                named after subjects listed in the caselist''',
        mandatory=True)

    subDir= cli.SwitchAttr(
        ['-s', '--subDir'],
        help='inside subject folder, if there is any subfolder before accessing structural image',
        mandatory=False)

    modality = cli.SwitchAttr(
        ['-t', '--type'],
        help='t1/t2',
        mandatory=True)

    imageSuffix= cli.SwitchAttr(
        ['-x', '--suffix'],
        help='image names should be imgDir/subDir/caseID+suffix',
        mandatory=True)


    caselist = cli.SwitchAttr(
        ['-l', '--caselist'],
        cli.ExistingFile,
        help='each line is a case inside the imageDir',
        mandatory=True)

    excelFile = cli.SwitchAttr(
        ['-e', '--excel'],
        cli.ExistingFile,
        help='''if visual_qc is done already, specify a .xlsx file containing 
                T1 and T2 visual scores, otherwise keep it empty. 
                This file is used for training or algorithm performance evaluation''',
        mandatory=False)


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

    train= cli.Flag(
        ['--train'],
        help= '''turn on this flag for training. During training, it extracts
                 features from all the images in a directory.
                 Registers the images to a reference image, creates foreground
                 mask of the reference image, and calculates intensity histogram of
                 non zero patches in the registered image. Edit the INPUT section
                 of structuralQC/config.ini file before running this application''',
        mandatory= False,
        default= False)

    def main(self):

        if self.modality != 't1' and self.modality != 't2':
            EXIT('Invalid structural mri, valid types: t1/t2')


        loadExternalCommands()


        if self.train:

            if self.register!=None or self.create or self.hist:

                feature_represent(self.imgDir, self.subDir, self.modality,
                            self.imageSuffix, self.caselist, str(self.excelFile),
                            self.register, self.create, self.hist, self.outDir)
            else:
                EXIT('None of the training options has been selected, turn on at least one of the flags.')


        else:

            t1 = time.time()
            batchProcessing(self.imgDir, self.subDir, self.modality,
                            self.imageSuffix, self.caselist, str(self.excelFile))

            print(f'Time taken in quality checking {time.time()-t1} seconds')



if __name__ == '__main__':
    batchQC.run()
