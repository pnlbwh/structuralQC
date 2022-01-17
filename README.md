![](doc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2584281.svg)](https://doi.org/10.5281/zenodo.2584281) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64-orange.svg)]()

*structuralQC* repository is developed by Tashrif Billah and Sylvain Bouix, Brigham and Women's Hospital (Harvard Medical School).

Table of Contents
=================

   * [Table of Contents](#table-of-contents)
   * [Structural MRI quality check tool](#structural-mri-quality-check-tool)
   * [Citation](#citation)
   * [Dependencies](#dependencies)
   * [Installation](#installation)
      * [1. Install prerequisites](#1-install-prerequisites)
         * [Python 3](#python-3)
         * [Template T1 and T2](#template-t1-and-t2)
      * [2. Install QC tool](#2-install-qc-tool)
      * [3 Download reference data](#3-download-reference-data)
      * [4. Configure your environment](#4-configure-your-environment)
   * [Tests](#tests)
   * [Processing](#processing)
      * [1. Individual processing](#1-individual-processing)
      * [2. Batch processing](#2-batch-processing)
         * [(i) Quality checking](#i-quality-checking)
         * [(ii) Training:](#ii-training)
            * [(a) Registration](#a-registration)
            * [(b) Feature extraction](#b-feature-extraction)
            * [(c) Train all together](#c-train-all-together)
   * [Advanced options](#advanced-options)
   * [Visual QC](#visual-qc)
   * [Multi threading](#multi-threading)
   * [Recommendation](#recommendation)


Table of Contents Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


# Structural MRI quality checking tool

structuralQC is a machine learning algorithm that predicts a structural mri (T1 or T2)
as a good or bad image. During acquisition of mri, it might be affected with 
motion, ghosting, or ringing aritficats. Further processing down any pipeline may be 
affected by the bad quality of the input image which is why quality assessment is important 
at the beginning.


The algorithm firstly masks an input image with foreground mask. Then, it slides a small 
cube throughout the volume, represents each cell in the cube with intensity histograms. After 
histogram representation of the image, it is compared against a library of good and bad images, 
and predicted as pass/fail.


# Citation

If you use our software in your research, please cite as below:

Tashrif Billah and Sylvain Bouix, Structural MRI Quality Checking Tool, https://github.com/pnlbwh/structuralQC, 
2018, DOI: 10.5281/zenodo.2584281


# Dependencies

* ANTs = 2.3.0
* numpy
* nibabel
* pandas
* scipy
* plumbum
* sklearn
* pynrrd


# Installation

## 1. Install prerequisites

### Python 3

Check system architecture

    uname -a # check if 32 or 64 bit


Download [Miniconda Python 3.6 bash installer](https://docs.conda.io/en/latest/miniconda.html) (32/64-bit based on your environment):
    
    sh Miniconda3-latest-Linux-x86_64.sh -b # -b flag is for license agreement

Activate the conda environment:

    source ~/miniconda3/bin/activate # should introduce '(base)' in front of each line


### Template T1 and T2

The quality check algorithm works by registering input image to a qood quality T1/T2 image. You may specify a 
site-specific T1/T2 image. If the image is not mask, you may specify a mask as well. Otherwise, you may 
use standard templates such as [MNI](http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_sym_09a_nifti.zip). 

* NOTE: unzip `mni_icbm152_nlin_asym_09a_nifti.zip` look for

```
mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii
mni_icbm152_nlin_sym_09a/mni_icbm152_t2_tal_nlin_sym_09a.nii
```

## 2. Install QC tool

Now that you have installed the prerequisite software, you are ready to install the pipeline:

    git clone https://github.com/pnlbwh/structuralQC.git
    conda env create -f environment.yml   # you may comment out any existing package from environment.yml
    conda activate structQC               # should introduce '(structQC)' in front of each line


Alternatively, if you already have ANTs, you can continue using your python environment by directly installing 
the prerequisite libraries:

    pip install -r requirements.txt --upgrade


## 3 Download reference data

A sample T1 and T2 image are provided for testing purpose. Besides, two reference features for T1 and T2 are provided 
for analyzing quality of an input structural MRI. You should download the reference data as follows:

    ./get_ref_data.sh

The above script should also update the configuration file [config.ini](cli-modules/config.ini)
pointing to the correct location of reference data.

## 4. Configure your environment

Make sure the following executables are in your path:

    antsApplyTransforms
    antsRegistrationSyNQuick.sh
    antsRegistration
    
You can check them as follows:

    which antsRegistrationSyNQuick.sh
    
If any of them does not exist, add that to your path:

    export PATH=$PATH:/directory/of/executable
    
`conda activate structQC` should already put the ANTs scripts in your path. However, if you choose to use pre-installed ANTs scripts, 
you may need to define [ANTSPATH](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS#set-path-and-antspath)



# Tests

After configuring your environment, you can download provided data and run tests:

    ./cli-modules/structuralQC.py -i ref_data/1001-t1w-xc.nrrd -t t1 --fixedImg mniTemplateT1.nii.gz -o /tmp/
    ./cli-modules/structuralQC.py -i ref_data/1001-t2w-xc.nrrd -t t2 --fixedImg mniTemplateT2.nii.gz -o /tmp/
    
If everything was done well so far, you should see quality score on the `stdout` and corresponding files saved in `/tmp/` 
with the same name prefix as that of the input structural image.


# Processing

When it comes to quality checking an MRI, we may want to analyze the quality of one MRI, or more likely, we may want to 
quality check a batch of data. The *structrualQC* toolbox is provided with both capability requiring less user intervention.


## 1. Individual processing

    Checks the quality of structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    
    Usage:
        structuralQC.py [SWITCHES]
    
    Meta-switches:
        -h, --help                          Prints this help message and quits
        --help-all                          Prints help messages of all sub-commands and quits
        -v, --version                       Prints the program's version and quits
    
    Switches:
        --fixedImg VALUE:ExistingFile       fixed image (i.e MNI atlas T1/T2 image); required
        --fixedMask VALUE:ExistingFile      mask of fixed image (i.e MNI atlas T1/T2 mask)
        -i, --input VALUE:ExistingFile      structural mri e.g. accepted formats: nhdr, nrrd, nii, and nii.gz; required
        -o, --out VALUE:str                 output directory (default: input img directory) where intermediate files are saved
        -t, --type VALUE:str                t1/t2; required



Given a structural image (T1 or T2), the algorithm can predict that as a good or bad image. 

> ./structuralQC.py -i image.nrrd -t t1 --fixedImage -o /tmp/

You can write a for loop/shell script to exploit the above for batch of data. However, you can also use 
[batch processing](#2.-batch-processing) to do it easily.

The program first looks for ansRegistration executables in system path. If they are not available, it exits immediately.

    antsRegistration found
    All executables are found, program will begin now ...

Then, it searches for an image with `reg` keyword in the input directory. If not found, registers the input image 
to the specified fixed image (in [config.ini](cli-modules/config.ini)).

    1001-t1w-xc.nrrd
    'reg' keyword is not present in input image. Registering with reference image ...
    Registration successful of 1001-t1w-xc.nrrd

Finally, upon checking quality, it prints out the result and saves it in the input or output (if specified) directory.

    Checking quality ...
    4, pass
    Time taken in structural QC 73.3800745010376 seconds


## 2. Batch processing

The merit of batch processing is the creation of a `.csv` file with predicted attributes. You can append a column 
on the right `Human validation` and put your own score/decision there. *Batch processing* is more versatile in a sense 
that it also lets you [train on your own data](#-(ii)-Training:).

> $ cli-modules/structuralQCbatch.py --help

    Checks the quality of all structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    
    Usage:
        structuralQCbatch.py [SWITCHES]
    
    Meta-switches:
        -h, --help                             Prints this help message and quits
        --help-all                             Prints help messages of all sub-commands and quits
        -v, --version                          Prints the program's version and quits
    
    Switches:
        -c, --caselist VALUE:ExistingFile      caseid of images to be quality checked; these caseids are present in visual qc
                                               excel file; required
        -e, --excel VALUE:ExistingFile         if visual_qc is done already, specify a .xlsx file containing T1 and T2 visual
                                               scores, otherwise keep it empty. This file is used for training or validating
                                               accuracy of prediction
        -f, --feature                          turn on this flag for obtaining histogram feature of registered image
        --fixedImg VALUE:ExistingFile          fixed image (i.e MNI atlas T1/T2 image); required
        --fixedMask VALUE:ExistingFile         mask of fixed image (i.e MNI atlas T1/T2 mask)
        -i, --imglist VALUE:ExistingFile       caseid of images to be quality checked; required
        -n, --numThreads VALUE:str             number of processes/threads to use (-1 for all available, may slow down your
                                               system); the default is 4
        -o, --out VALUE:str                    output directory (default: input image directory) where feature histograms,
                                               registered images, and foreground masks are saved.; required
        -r, --register                         turn on this flag to register images to the reference image
        -t, --type VALUE:str                   t1/t2; required
        --train                                turn on this flag for training. During training, it extracts features from all
                                               the images in a directory. First, it registers the images to a reference image,
                                               and then calculates intensity histogram of non zero patches in the registered
                                               image. If necessary, edit the INPUT section in lib/config.ini file before
                                               running this application



### (i) Quality checking

In addition to the arguments discussed for [individual processing](#1.-individual-processing), specify an imagelist: 
    
    -i, --imglist VALUE:ExistingFile
    
with absolute path of images you want to quality check. Also, specify a caselist with caseids that will be used to 
organize quality scores in a *csv* file:
    
    -c, --caselist VALUE:ExistingFile

In training mode, caseids must correspond to the *Subject ID* column in [visual qc excel file](#visual-qc). 

The following is a sample command for quality checking of a batch of data:
    
    ./structuralQCbatch.py \
    -i ~/Documents/test_data.csv \
    -c ~/Documents/test_data/caselist.txt \
    --fixedImg ~/Documents/test_data/1001-t1w-xc.nrrd -r \
    -e ~/Documents/test_data/visual_qc.xlsx \
    -t t1 -f \
    -o ~/Documents/tempMaskOutput


### (ii) Training:

*Batch processing* lets you train on your own data. See [advanced option](#advanced-options) before training on your own 
data. In training mode, caseids must correspond to the *Subject ID* column in [visual qc excel file](#visual-qc).  

> $ cli-modules/structuralQCbatch.py --help

    Checks the quality of all structural mri (T1/T2).
    Predicts a score for the mri, and gives a pass/fail recommendation.
    
    Usage:
        structuralQCbatch.py [SWITCHES]
    
    Meta-switches:
        -h, --help                             Prints this help message and quits
        --help-all                             Prints help messages of all sub-commands and quits
        -v, --version                          Prints the program's version and quits
    
    Switches:
        -c, --caselist VALUE:ExistingFile      caseid of images to be quality checked; these caseids are present in visual qc
                                               excel file; required
        -e, --excel VALUE:ExistingFile         if visual_qc is done already, specify a .xlsx file containing T1 and T2 visual
                                               scores, otherwise keep it empty. This file is used for training or validating
                                               accuracy of prediction
        -f, --feature                          turn on this flag for obtaining histogram feature of registered image
        --fixedImg VALUE:ExistingFile          fixed image (i.e MNI atlas T1/T2 image); required
        --fixedMask VALUE:ExistingFile         mask of fixed image (i.e MNI atlas T1/T2 mask)
        -i, --imglist VALUE:ExistingFile       caseid of images to be quality checked; required
        -n, --numThreads VALUE:str             number of processes/threads to use (-1 for all available, may slow down your
                                               system); the default is 4
        -o, --out VALUE:str                    output directory (default: input image directory) where feature histograms,
                                               registered images, and foreground masks are saved.; required
        -r, --register                         turn on this flag to register images to the reference image
        -t, --type VALUE:str                   t1/t2; required
        --train                                turn on this flag for training. During training, it extracts features from all
                                               the images in a directory. First, it registers the images to a reference image,
                                               and then calculates intensity histogram of non zero patches in the registered
                                               image. If necessary, edit the INPUT section in lib/config.ini file before
                                               running this application


The following are sample commands for training the algorithm (specify the `--train` flag):

#### (a) Registration

Specify the `-r` flag to register a test images to the template. 
Features are obtained afterwards.

    ./structuralQCbatch.py \
    -i ~/Documents/test_data.csv \
    -c ~/Documents/test_data/caselist.txt \
    --fixedImg ~/Documents/test_data/1001-t1w-xc.nrrd -r \
    -e ~/Documents/test_data/visual_qc.xlsx \
    -t t1 \ 
    -o ~/Downloads/tempMaskOutput --train

#### (b) Feature extraction

Each registered test image is represented by a histogram. 
You may train the algorithm by varying some of the [advanced option](#advanced-options) without registering again. 
Specify the `-f` flag for histogram calculation. This option is useful 
when you want to train with a different set of parameters (see [config.ini](./config.ini)) 
keeping the fixed image and registered image same.

    ./structuralQCbatch.py \
    -i ~/Documents/test_data.csv \
    -c ~/Documents/test_data/caselist.txt \
    -e ~/Documents/test_data/visual_qc.xlsx \
    -t t1 -f \
    -o ~/Downloads/tempMaskOutput --train


#### (c) Train all together

The following sample command comprises all the training steps above.

    ./structuralQCbatch.py \
    -i ~/Documents/test_data.csv \
    -c ~/Documents/test_data/caselist.txt \
    --fixedImg ~/Documents/test_data/1001-t1w-xc.nrrd -r \
    -e ~/Documents/test_data/visual_qc.xlsx \
    -t t1 -f \
    -o ~/Documents/tempMaskOutput --train


After training is complete, `config.ini` file should update automatically (if there are changes). If it
does not point to the right paths, just update `config.ini` manually.


# Advanced options

There are some other parameters in `config.ini` as follows:

    [DEFAULT]
    points = 20
    nx = 8
    ny = 8
    nz = 8
    eta = 0.9
    sx = 2
    sy = 2
    sz = 2
    metric = PEARSON
    decisionfactor = 2

`points` are the number of bins for histogram in each cell of the small cube
`n*` are the dimensions of the small cube that we slide along the 3D image volume
`eta` is the degree of overlap required for comparing each patch to the library images
`s*` is the stride taken to get the next small cube. If you set `s*` to greater than 1 (usually 2 or 3),
the prediction will be faster
`metric` currently supports `BC`, `MSE`, `KL` respectively for Bhattacharya distance, mean squared error, 
and KL divergence
`decisionfactor` is the factor that determines threshold for predicting an image as pass. For example, 
if 1 is the worst and 4 is the best, then a `decisionfactor` of 2 will set halfway (2) as the threshold:

    score_range= np.ptp(discreteScores)+1 if min(discreteScores)>0 else np.ptp(discreteScores)
    quality= 'pass' if predicted_score>score_range/decisionFactor else 'fail'


# Visual QC

In training mode, visual quality scores are required to train the algorithm. As occurs for most training, someone 
has to visually look at a batch of data and give it `discreteScores`. In our training, we have used `[1,2,3,4]` as 
the discrete scores while `1` is for worst i.e. an MRI affected by severe ringing, ghosting, motion, and signal drop. 
On the other hand, `4` is for a good quality MRI free from noticeable artifacts. The scores should be in an excel file 
as follows:

| Subject ID | t1 score | t2 score |
| --- | --- | --- |
| 1001 |  1 | 4 |
| 1002 | 3 | 2 |
| ... | | |
| ... | | |

Make sure to properly write the header:
    
    | Subject ID | t1 score | t2 score |
    
The caseids in the caselist should be same as the ones used under Subject ID column in the excel file.

# Multi threading

Batch processing can be multi-threaded with number of cores/processes specified against 
    
    -n, --numThreads VALUE:str    number of processes/threads to use (-1 for all available, may slow down your
                                  system); the default is 4


Multi threading should enable a faster execution of batch processing.

# Recommendation

Source:

Training image for T1: mindcontrol HBN data
Training image for T2: DIAGNOSE_CTE_U01 data

Current results:

Detection accuracy of bad images: ~95%
Detection accuracy of good images: ~70%

Percentage confusion matrix:

T1 images from mindcontrol HBN data

|  | Bad | Good |
| --- | --- | --- |
| Bad |  95 | 5 |
| Good | 47 | 53 |


That means there is a significant likelihood that good images fall in the bad bin. But, bad images rarely fall in the
good bin.


T2 images from DIAGNOSE_CTE_U01 data


|  | Bad | Good |
| --- | --- | --- |
| Bad |  99 | 1 |
| Good | 0 | 100 |


The above data was not balanced between good and bad images. There might be overfitting or inconsistency 
among sites/raters.


So the recommendation is to **visually observe** images that are given a **bad** label 
(because good images have a significant chance of being classified as bad by the algorithm).
