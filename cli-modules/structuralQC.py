#!/usr/bin/env python

from plumbum import cli
from loadFile import loadExecutable, loadExternalCommands
from errorChecking import EXIT, keyPrompt
import time, configparser
from os.path import abspath, dirname, basename, join as pjoin

SCRIPTDIR= abspath(dirname(__file__))
config = configparser.ConfigParser()
config.read(pjoin(SCRIPTDIR, 'config.ini'))

class QC(cli.Application):

    """Checks the quality of structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    """

    img = cli.SwitchAttr(
        ['-i', '--input'],
        cli.ExistingFile,
        help='structural mri e.g. accepted formats: nhdr, nrrd, nii, and nii.gz',
        mandatory=True)

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

    modality= cli.SwitchAttr(
        ['-t', '--type'],
        help= 't1/t2',
        mandatory= True)

    outDir = cli.SwitchAttr(
        ['-o', '--out'],
        help='''output directory (default: input img directory)
                where intermediate files are saved''',
        mandatory=False)


    def main(self):

        self.img= str(self.img)
        self.fixedImg= str(self.fixedImg)
        self.fixedMask= str(self.fixedMask)
        self.modality= self.modality.lower()

        if self.modality=='t1':
            config['TRAINING']['fixedImaget1'] = self.fixedImg
            config['TRAINING']['fixedMaskt1'] = self.fixedMask

        elif self.modality=='t2':
            config['TRAINING']['fixedImaget2'] = self.fixedImg
            config['TRAINING']['fixedMaskt2'] = self.fixedMask

        else:
            EXIT('Invalid structural mri, valid types: t1/t2')



        # check t1/t2 consistency
        if self.modality not in basename(self.fixedImg).lower():
            print('Warning: Are you sure about modality and referenceImage?')
            keyPrompt()

        # write back the config.ini after everything
        with open(pjoin(SCRIPTDIR, 'config.ini'), 'w') as f:
            config.write(f)


        loadExternalCommands()
        
        from calculation import processImage

        t1= time.time()
        processImage(self.img, self.outDir, self.modality)
        print(f'Time taken in structural QC {time.time()-t1} seconds')


if __name__ == '__main__':
    QC.run()
