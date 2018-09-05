#!/usr/bin/env python

import configparser
import os
import pandas as pd
import numpy as np
import multiprocessing

from loadFile import loadExcel, loadCaseList, loadExternalCommands
from calculation import processImage

from sklearn.metrics import confusion_matrix

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))

imageFolder= config['INPUT']['imageFolder']
caselist = config['INPUT']['caselist']
subFolder= config['INPUT']['subFolder']
imageSuffix= config['INPUT']['imageSuffix']
modality= config['INPUT']['modality']

discreteScores = [int(x) for x in config['TRAINING']['discreteScores'].split(',')]

def EXIT():
    print("Result evaluation failed")
    exit(1)

def subject_prediction(sub):

    img=os.path.join(imageFolder, sub, subFolder, sub+imageSuffix)
    prediction= processImage(img, 'None', 'None', modality)

    return prediction


def resultEvaluation(subjects, predicted_scores, excelFile):

    # read the Subject ID and {modality} column
    cases, visual_scores= loadExcel(excelFile, modality)

    # error checking
    if len(subjects)!=len(cases):
        print("The number of given and predicted cases are not equal")
        EXIT()

    if len(cases)!= len(set(cases)) or len(subjects)!= len(set(subjects)):
        print("Possible case duplication in caselist or visual_qc file")
        EXIT()

    # always a good practice to avoid list.append(object)
    true_scores = [0]*len(subjects)
    # cases might be in different order than subjects
    for i, s in enumerate(subjects):

        try:
            ind= cases.index(s)
        except ValueError:
            print("Case missing, compare the caselist.txt and visual_qc.xlsx")
            EXIT()

        true_scores[i]= visual_scores[ind]

    # reshaping and data type consistency are required
    print("Confusion matrix (columns are true labels, rows are predicted labels):")
    print("Visual discrete scores are: ", discreteScores)
    print(confusion_matrix(true_scores, predicted_scores, labels= discreteScores))



def main():

    loadExternalCommands()

    subjects = loadCaseList(caselist)
    num_sub = len(subjects)

    pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

    res = pool.map_async(subject_prediction, subjects)
    value = res.get()
    predicted_scores= [value[i] for i in range(num_sub)]

    pool.close()
    pool.join()


    df= pd.DataFrame({'Case #': subjects,
                  f'Predicted score ({min(discreteScores)} being worst, {max(discreteScores)} being best)': predicted_scores})

    df.to_csv(os.path.join(imageFolder, f'{modality}_QC_scores.csv'), index= False)

    # another way of saving data
    '''
    f = open(os.path.join(os.path.dirname(caselist), f'{modality}_QC_scores.csv'), 'w')
    discreteScores = [int(x) for x in config['TRAINING']['discreteScores'].split(',')]
    f.write(f'Case #, Predicted score ({min(discreteScores)} being worst, {max(discreteScores)} being best) \n')
    for i in range(num_sub):
        f.write(subjects(i) + ',' + str(predicted_scores) + '\n')

    f.close()
    '''

    excelFile= config['INPUT']['visual_qc_excel_file']
    if excelFile:
        resultEvaluation(subjects, predicted_scores, excelFile)


if __name__=="__main__":
    main()