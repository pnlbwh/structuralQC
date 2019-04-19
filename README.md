![](doc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2584281.svg)](https://doi.org/10.5281/zenodo.2584281) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64-orange.svg)]()

*structuralQC* repository is developed by Tashrif Billah and Sylvain Bouix, Brigham and Women's Hospital (Harvard Medical School).

Table of Contents
=================

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
   * [Individual processing](#individual-processing)
   * [Batch processing](#batch-processing)
   * [Training:](#training)
   * [Testing](#testing)
   * [Caselist generation](#caselist-generation)
   * [Advanced options](#advanced-options)
   * [Recommendation](#recommendation)

Table of Contents Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


# Structural MRI quality check tool

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

Tashrif Billah and Sylvain Bouix, Structural MRI Quality Check Tool, https://github.com/pnlbwh/structuralQC, 
2018, DOI: 10.5281/zenodo.2584281


# Dependencies

* ANTs
* numpy
* scipy
* nibabel
* pynrrd
* plumbum
* pandas

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
use standard templates such as [MNI](http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_asym_09a_nifti.zip). 

* NOTE: unzip `mni_icbm152_nlin_asym_09a_nifti.zip` look for
     
    mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii
    mni_icbm152_nlin_sym_09a/mni_icbm152_t2_tal_nlin_sym_09a.nii


## 2. Install QC tool

Now that you have installed the prerequisite software, you are ready to install the pipeline:

    git clone https://github.com/pnlbwh/structuralQC.git
    conda create -f environmnet.yml     # you may comment out any existing package from environment.yml
    conda activate structQC             # should introduce '(structQC)' in front of each line


Alternatively, if you already have ANTs, you can continue using your python environment by directly installing 
the prerequisite libraries:

    pip install -r requirements.txt --upgrade


## 3 Download reference data

    ./get_ref_data.sh

## 4. Configure your environment

Make sure the following executables are in your path:

    antsApplyTransforms
    antsRegistrationSyNQuick.sh
    antsRegistration
    antsRegistrationSyNMI.sh
    
You can check them as follows:

    which antsRegistrationSyNMI.sh
    
If any of them does not exist, add that to your path:

    export PATH=$PATH:/directory/of/executable
    
`conda activate structQC` should already put the ANTs scripts in your path. However, if you choose to use pre-installed ANTs scripts, 
you may need to define [ANTSPATH](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS#set-path-and-antspath)



# Tests

After configuring your environment, you can download provided data and run tests:

    ./cli-modules/structuralQC.py -i t1_test_image.nrrd -t t1 --fixedImage mniTemplateT1.nii.gz
    ./cli-modules/structuralQC.py -i t2_test_image.nrrd -t t2 --fixedImage mniTemplateT2.nii.gz
    
    
    
# ---------------------------------------------------------------------------------------------------------------------    
unzipping the source code, update the configuration file [config.ini](./config.ini)
to point to the correct location of fixed image, training masks, and histograms.

> unzip structuralQC.zip .

> tar -xzvf training_data.tar.gz .

*Note: There is seperate training data for the `T1` and `T2` images. So, be sure to point to the proper location.


After the above steps, you can test your installation:




If everything is done well, some files will be created in the training_data directory. 
You can observe them to see the results.



# Individual processing

```
Checks the quality of structural mri (T1/T2).
Predicts a score for the mri, and gives a pass/fail recommendation.

Usage:
    structuralQC.py [SWITCHES] 

Meta-switches:
    -h, --help                          Prints this help message and quits
    --help-all                          Print help messages of all subcommands and quit
    -v, --version                       Prints the program's version and quits

Switches:
    -i, --input VALUE:ExistingFile      structural mri e.g. accepted formats: nhdr, nrrd, nii, and nii.gz; required
    -m, --mask VALUE:ExistingFile       foreground mask for structural mri (mask extracted after structural mri being aligned with reference
                                        mri), accepted formats: nhdr, nrrd, nii, and nii.gz, if not provided then looks for default: prefix-
                                        fore-mask* in input directory, if default is not available, then creates the foreground mask
    -o, --out VALUE:str                 output directory (default: input img directory) where intermediate files are saved
    -t, --type VALUE:str                t1/t2; required


```


Given a structural image (T1 or T2), the algorithm can predict that as a good or bad image. 

> ./structuralQC.py -i image.nrrd -t t1 --fixedImage -o /tmp/


You can write a shell script to exploit the above for batch of data. However, you can also use the following batch processing to do it 
easily.



The program first looks for ansRegistration executables in system path. If they are not available, it exits immediately.

```
Slicer found
antsRegistration found
All executables are found, program will begin now ...

```

Then, it searches for an image with `reg` keyword in the input directory. If not found, registers the input image 
to the specified fixed image (in [config.ini](./config.ini)). Again, it looks for mask and creates mask if needed.

```
~/Documents/structural_mri/1001/raw/1001-t1w-xc.nrrd
'reg' keyword is not present in input image. Registering with reference image ...
Registration successful of 1001-t1w-xc.nrrd
Creating mask ...
Foreground mask created of 1001-t1w-xc-reg.nii.gz

```

Finally, upon checking quality, it prints out the result and saves it in the input or output (if specified) directory.

```
Checking quality ...
4, pass
Time taken in structural QC 73.3800745010376 seconds
```


# Batch processing

The merit of batch processing is the creation of a `.csv` file with predicted attributes. You can append a column 
on the right `Human validation` and put your own score/decision there.


# Training:

```
Checks the quality of all structural mri (T1/T2).
Predicts a score for the mri, and gives a pass/fail recommendation.

Usage:
    structuralQCbatch.py [SWITCHES] 

Meta-switches:
    -h, --help                                  Prints this help message and quits
    --help-all                                  Print help messages of all subcommands and quit
    -v, --version                               Prints the program's version and quits

Switches:
    -c, --createMask                            Turn on this flag for creating mask of the registered image
    -e, --excel VALUE:ExistingFile              if visual_qc is done already, specify a .xlsx file containing T1 and T2 visual scores,
                                                otherwise keep it empty. This file is used for training or algorithm performance evaluation
    -f, --feature                               Turn on this flag for obtaining histogram feature of registered image
    -i, --inputDir VALUE:ExistingDirectory      structural image folder inside image folder, there should be other folders named after
                                                subjects listed in the caselist; required
    -l, --caselist VALUE:ExistingFile           each line is a case inside the imageDir; required
    -o, --out VALUE:str                         output directory (default: input image directory) where feature histograms, registered
                                                images, and foreground masks are saved.
    -r, --referenceImage VALUE:str              Use this option for registering input images to the reference image, specify the reference
                                                image.
    -s, --subDir VALUE:str                      inside subject folder, if there is any subfolder before accessing structural image; the
                                                default is .
    -t, --type VALUE:str                        t1/t2; required
    --train                                     turn on this flag for training. During training, it extracts features from all the images in
                                                a directory. Registers the images to a reference image, creates foreground mask of the
                                                reference image, and calculates intensity histogram of non zero patches in the registered
                                                image. Edit the INPUT section of structuralQC/config.ini file before running this application
    -x, --suffix VALUE:str                      image names should be imgDir/subDir/caseID+suffix; required


```


The following are example arguments for some of the above flags:


```
# structural image folder
# inside image folder, there should be a folder named after subjects listed in the excel file
imageFolder= ~/Documents/structural_mri

# each line is a case inside the imageFolder
caselist= ~/Documents/structural_mri/caselist.txt

# inside subject folder, if there is any subfolder before accessing structural image
subFolder= raw

# specify image suffix after the subject prefix
imageSuffix= *t2*reg.nii.gz

# t1/t2
modality= t2
```



The following are sample commands for training the algorithm (specify the `--train` flag):

1. register the test images to a fixed image

Specify the `-r` flag followed by a fixed image to register test images to a good image. 
Mask and histograms are created afterwards.


Note: Specify the image suffix in a way that represents all the testing images. 
The input `imageFolder/sub_name/subFolder` is searched for images `sub_name+imageSuffix`. 
So, put an `*` wherever it doesn't hurt such as `-x *imageSuffix*reg*nii.gz`.


```
./structuralQCbatch.py \
-i ~/Documents/test_data \
-l ~/Documents/test_data/caselist.txt -s raw \
-r ~/Documents/test_data/1001-t1w-xc.nrrd \
-e ~/Documents/test_data/visual_qc.xlsx \
-t t1 -x -t1w-xc.nrrd \ 
-o ~/Downloads/tempMaskOutput --train
```
                        
                             
2. create foreground masks of the registered test images

Specify the `-m` flag for foreground mask creation. This option is useful 
for recalculating mask with a different threshold (see [masking.py](./cli-modules/masking.py) but same registered image.
Since mask affects the histograms, the histograms are recreated after mask creation.


```
./structuralQCbatch.py \
-i ~/Downloads/tempMaskOutput \
-l ~/Documents/test_data/caselist.txt \
-e ~/Documents/test_data/visual_qc.xlsx \
-t t1 -x -t1-xc-reg.nii.gz -c \
-o ~/Downloads/tempMaskOutput --train
```


3. represent each registered test image by histogram

Specify the `-f` flag for histogram calculation. This option is useful 
when you want to train with a different set of parameters (see [config.ini](./config.ini)) 
keeping the fixed image, registered image, and mask same.

```
./structuralQCbatch.py \
-i ~/Documents/test_data -s raw \
-l ~/Documents/test_data/caselist.txt \
-e ~/Documents/test_data/visual_qc.xlsx \
-t t1 -x -t1-reg.nii.gz -f \
-o ~/Downloads/tempMaskOutput --train
```


4. train all together

The following sample command comprises all the training steps above.

```
./structuralQCbatch.py \
-i ~/Documents/test_data -s raw \
-l ~/Documents/test_data/caselist.txt \
-r ~/Documents/test_data/1001-t1w-xc.nrrd \
-e ~/Documents/test_data/visual_qc.xlsx \
-t t1 -x -t1w-xc.nrrd -c -f \
-o ~/Documents/tempMaskOutput --train
```


After training is complete, `config.ini` file should update automatically (if there are changes). If it
does not point to the right paths, just update `config.ini` manually.


# Testing

After training is done, the `config.ini` file will update automatically pointing to the
fixed image, training image mask folder, and reference histogram. To use the same registered 
images for testing, specify the test image suffix as `{modality}-reg.nii.gz`:

```
./structuralQCbatch.py \
-i ~/Documents/test_data -s raw \
-l ~/Documents/test_data/caselist.txt \
-e ~/Documents/test_data/visual_qc.xlsx \
-t t1 -x -t1-reg.nii.gz
```

To test a different set of images (register, create mask, calculate histogram), specify the 
imageFolder, subFolder, sub_name, and imageSuffix.


```
./structuralQCbatch.py \
-i ~/Documents/mindcontrol-hbn/t1_images \
-l ~/Documents/mindcontrol-hbn/t1_images/caselist.txt \
-e ~/Documents/mindcontrol-hbn/visual_qc_t1.xlsx \
-t t1 -x *_T1w.nii.gz
```



# Caselist generation

```
cd image/directory/
ls -d first-few-letters-of-subject-folder-* > caselist.txt
```




# Advanced options

There are some other parameters in `config.ini` as follows:

```
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
```


`points` are the number of bins for histogram in each cell of the small cube
`n*` are the dimensions of the small cube that we slide along the 3D image volume
`eta` is the degree of overlap required for comparing each patch to the library images
`s*` is the stride taken to get the next small cube. If you set `s*` to greater than 1 (usually 2 or 3),
the prediction will be faster
`metric` currently supports `BC`, `MSE`, `KL` respectively for Bhattacharya distance, mean squared error, 
and KL divergence
`decisionfactor` is the factor that determines threshold for predicting an image as pass. For example, 
if 1 is the worst and 4 is the best, then a `decisiofactor` of 2 will set halfway (2) as the threshold:


```
score_range= np.ptp(discreteScores)+1 if min(discreteScores)>0 else np.ptp(discreteScores)
quality= 'pass' if predicted_score>score_range/decisionFactor else 'fail'
```


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


So the recommendation is to visually observe images that are given a bad label 
(because good images have a significant chance of being classified as bad by the algorithm).

