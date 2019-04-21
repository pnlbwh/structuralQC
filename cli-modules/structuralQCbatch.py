#!/usr/bin/env python

from plumbum import cli
from batchProcessing import batchProcessing
from loadFile import loadExecutable, loadExternalCommands, loadCaseList, loadImageList
from feature_represent import feature_represent
from errorChecking import EXIT, keyPrompt
import time
import configparser
from psutil import cpu_count

from os.path import isdir, abspath, dirname, basename, join as pjoin
from os import makedirs

SCRIPTDIR= abspath(dirname(__file__))
config = configparser.ConfigParser()
config.read(pjoin(SCRIPTDIR, 'config.ini'))

class batchQC(cli.Application):
    """Checks the quality of all structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    """

    modality = cli.SwitchAttr(
        ['-t', '--type'],
        help='t1/t2',
        mandatory=True)

    imglist = cli.SwitchAttr(
        ['-i', '--imglist'],
        cli.ExistingFile,
        help='caseid of images to be quality checked',
        mandatory=True)

    caselist = cli.SwitchAttr(
        ['-c', '--caselist'],
        cli.ExistingFile,
        help='caseid of images to be quality checked; these caseids are present in visual qc excel file',
        mandatory=True)

    excelFile = cli.SwitchAttr(
        ['-e', '--excel'],
        cli.ExistingFile,
        help='''if visual_qc is done already, specify a .xlsx file containing 
                T1 and T2 visual scores, otherwise keep it empty. 
                This file is used for training or validating accuracy of prediction''',
        default='',
        mandatory=False)


    fixedImg = cli.SwitchAttr(
        ['--fixedImg'],
        cli.ExistingFile,
        help='fixed image (i.e MNI atlas T1/T2 image)',
        mandatory=True)

    fixedMask = cli.SwitchAttr(
        ['--fixedMask'],
        cli.ExistingFile,
        help='mask of fixed image (i.e MNI atlas T1/T2 mask)',
        mandatory=False,
        default='')

    register= cli.Flag(
        ['-r', '--register'],
        help= 'turn on this flag to register images to the reference image',
        mandatory= False,
        default= False)

    hist= cli.Flag(
        ['-f', '--feature'],
        help= 'turn on this flag for obtaining histogram feature of registered image',
        mandatory= False,
        default= False)

    outDir = cli.SwitchAttr(
        ['-o', '--out'],
        help='''output directory (default: input image directory)
                where feature histograms, registered images,
                and foreground masks are saved.''',
        mandatory=True)

    train = cli.Flag(['--train'],
        help='''turn on this flag for training. During training, it extracts
                features from all the images in a directory. First, it registers 
                the images to a reference image, and then calculates intensity histogram of
                non zero patches in the registered image. If necessary, edit the INPUT section
                in lib/config.ini file before running this application''',
        mandatory=False,
        default=False)

    N_CPU = cli.SwitchAttr(
        ['-n', '--numThreads'],
        help= 'number of processes/threads to use (-1 for all available, may slow down your system)',
        default= 4)



    def main(self):

        self.excelFile= str(self.excelFile)
        self.fixedImg= str(self.fixedImg)
        self.fixedMask= str(self.fixedMask)
        self.modality= self.modality.lower()
        self.outDir= abspath(self.outDir)

        if self.modality=='t1':
            config['TRAINING']['fixedImaget1'] = self.fixedImg
            config['TRAINING']['fixedMaskt1'] = self.fixedMask

        elif self.modality=='t2':
            config['TRAINING']['fixedImaget2'] = self.fixedImg
            config['TRAINING']['fixedMaskt2'] = self.fixedMask

        else:
            EXIT('Invalid structural mri, valid types: t1/t2')

        if self.train and not self.excelFile:
            EXIT('a .xlsx file containing T1 and T2 visual scores is required in training mode')

        config['TRAINING']['visual_qc_excel_file'] = self.excelFile

        if self.N_CPU==-1:
            self.N_CPU= cpu_count()

        config['RESOURCE']['N_CPU'] = str(self.N_CPU)


        # write back the config.ini after everything
        with open(pjoin(SCRIPTDIR, 'config.ini'), 'w') as f:
            config.write(f)


        loadExternalCommands()


        # check t1/t2 consistency
        if self.modality not in basename(self.fixedImg).lower():
            print('Warning: Are you sure about modality and referenceImage?')
            keyPrompt()


        imgs = loadImageList(self.imglist)
        subjects = loadCaseList(self.caselist)


        if not isdir(abspath(self.outDir)):
            makedirs(self.outDir)


        t1 = time.time()
        if self.train:

            if not (self.hist or self.register):
                EXIT('specify --feature and/or --register mode')

            feature_represent(imgs, subjects, self.register, self.hist, self.modality, self.outDir)
            print(f'Time taken in feature extraction for training {time.time()-t1} seconds')

        else:
            batchProcessing(imgs, subjects, self.modality, self.outDir)
            print(f'Time taken in quality checking {time.time()-t1} seconds')



if __name__ == '__main__':
    batchQC.run()
