# TODO: Specify the interpreter here

from plumbum import cli
from calculation import processImg
import sys, os

# /structuralQC/ should be added to PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class QC(cli.Application):

    """Checks the quality of structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    """

    img = cli.SwitchAttr(
        ['-i', '--input'],
        cli.ExistingFile,
        help='structural mri e.g. accepted formats: nhdr, nrrd, nii, and nii.gz',
        mandatory=True)

    modality= cli.SwitchAttr(
            ['-t', '--type'],
            help= 'T1/T2',
            mandatory= True)

    mask = cli.SwitchAttr(
        ['-m', '--mask'],
        cli.ExistingFile,
        help='''foreground mask for structural mri (mask extracted after structural
            mri being aligned with reference mri), accepted formats: nhdr, nrrd, nii, and nii.gz, 
            if not provided then looks for default: prefix-fore-mask* in input directory,
            if default is not available, then creates the foreground mask''',
        mandatory=False)

    outDir = cli.SwitchAttr(
        ['-o', '--out'],
        help='''output directory (default: input img directory)
                where intermediate files are saved
                ''',
        mandatory=False)


    def main(self):

        self.img= str(self.img)
        self.mask= str(self.mask)
        self.outDir= str(self.outDir)
        self.modality= self.modality.lower()

        if self.modality != 't1' or self.modality != 't2':
            print('Invalid structural mri, valid types: t1/t2')
            exit(1)

        processImg(self.img, self.mask, self.outDir, self.modality)

if __name__ == '__main__':
    QC.run()
