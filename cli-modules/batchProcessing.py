#!/usr/bin/env python

import configparser
import os, time
import pandas as pd
import multiprocessing
import ast


from loadFile import loadExcel, loadCaseList
from calculation import processImage
from errorChecking import errorChecking, EXIT

from sklearn.metrics import confusion_matrix
import glob

'''
config_input = configparser.ConfigParser()
config_input.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config_input.ini')))
imageFolder= config_input['INPUT']['imageFolder']
caselist = config_input['INPUT']['caselist']
subFolder= config_input['INPUT']['subFolder']
imageSuffix= config_input['INPUT']['imageSuffix']
modality= config_input['INPUT']['modality']
excelFile= config_input['INPUT']['visual_qc_excel_file']
'''

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
discreteScores = ast.literal_eval(config['TRAINING']['discreteScores'])


def subject_prediction(sub):

    # By this design, the user should have more flexibility in naming the files
    # Also, it should be easier to reuse registered images and masks

    # inside imageFolder, images are grouped by subject folders
    # imageSuffix should be "*t1*nii.gz" or "*t1*-reg.nii.gz" based on unregistered or registered image
    temp= glob.glob(os.path.join(imageFolder, sub, subFolder, sub+imageSuffix))
    if len(temp)>1:
        EXIT(f"Multiple {modality} images found with the provided suffix, make that unique, and try again.")
    img= temp[0]
    # processImage(imgPath, maskPath, directory, modality)
    prediction= processImage(img, 'None', '', modality)

    return prediction


def resultEvaluation(subjects, predicted_scores):

    # read the Subject ID and {modality} column
    cases, visual_scores= loadExcel(excelFile, modality)

    errorChecking(subjects, cases)

    true_scores= [visual_scores[cases.index(s)] for s in subjects]

    # reshaping and data type consistency are required
    print("Confusion matrix (columns are true labels, rows are predicted labels):")
    print("Visual discrete scores are: ", discreteScores)
    print(confusion_matrix(true_scores, predicted_scores, labels= discreteScores))



def batchProcessing(imgDir, subDir, type,
                    suffix, cases, xlsxFile):

    global imageFolder, subFolder, modality, imageSuffix, caselist, excelFile

    imageFolder= imgDir
    subFolder= subDir
    modality= type
    imageSuffix= suffix
    caselist= cases
    excelFile= xlsxFile

    if not subFolder:
        subFolder= '.'

    subjects = loadCaseList(caselist)
    num_sub = len(subjects)

    pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

    res = pool.map_async(subject_prediction, subjects)
    attributes  = res.get()
    predicted_scores= [attributes[i][0] for i in range(num_sub)]
    predicted_quality = [attributes[i][1] for i in range(num_sub)]

    pool.close()
    pool.join()


    df= pd.DataFrame({'Case #': subjects,
            f'Predicted score ({min(discreteScores)} being worst, {max(discreteScores)} being best)': predicted_scores,
            'Quality': predicted_quality})

    df.to_csv(os.path.join(imageFolder, f'{modality}_QC_scores.csv'), index= False)

    # another way of saving data
    '''
    f = open(os.path.join(os.path.dirname(caselist), f'{modality}_QC_scores.csv'), 'w')
    f.write(f'Case #, Predicted score ({min(discreteScores)} being worst, {max(discreteScores)} being best) \n')
    for i in range(num_sub):
        f.write(subjects(i) + ',' + str(predicted_scores) + '\n')

    f.close()
    '''

    if excelFile:
        resultEvaluation(subjects, predicted_scores)

def main():
    pass
    # run test qc on a small set of images


if __name__=="__main__":
    main()
