#!/usr/bin/env python

import configparser
import os, time
import pandas as pd
import multiprocessing
import ast


from loadFile import loadExcel, loadCaseList, loadExternalCommands
from calculation import processImage
from errorChecking import errorChecking, EXIT

from sklearn.metrics import confusion_matrix

config_input = configparser.ConfigParser()
config_input.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config_input.ini')))
imageFolder= config_input['INPUT']['imageFolder']
caselist = config_input['INPUT']['caselist']
subFolder= config_input['INPUT']['subFolder']
imageSuffix= config_input['INPUT']['imageSuffix']
modality= config_input['INPUT']['modality']
excelFile= config_input['INPUT']['visual_qc_excel_file']

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
discreteScores = ast.literal_eval(config['TRAINING']['discreteScores'])


def subject_prediction(sub):

    img=os.path.join(imageFolder, sub, subFolder, sub+imageSuffix)
    # processImage(imgPath, maskPath, directory, modality)
    prediction= processImage(img, 'None', '', modality)

    return prediction


def resultEvaluation(subjects, predicted_scores, excelFile):

    # read the Subject ID and {modality} column
    cases, visual_scores= loadExcel(excelFile, modality)

    errorChecking(subjects, cases)

    true_scores= [visual_scores[cases.index(s)] for s in subjects]

    # reshaping and data type consistency are required
    print("Confusion matrix (columns are true labels, rows are predicted labels):")
    print("Visual discrete scores are: ", discreteScores)
    print(confusion_matrix(true_scores, predicted_scores, labels= discreteScores))



def main():

    t1= time.time()

    loadExternalCommands()

    subjects = loadCaseList(caselist)
    num_sub = len(subjects)

    pool = multiprocessing.Pool()  # Use all available cores, otherwise specify the number you want as an argument

    res = pool.map_async(subject_prediction, subjects)
    value = res.get()
    predicted_scores= [value[i] for i in range(num_sub)]

    pool.close()
    pool.join()

    print(f'Time taken in quality checking {time.time()-t1} seconds')


    df= pd.DataFrame({'Case #': subjects,
                  f'Predicted score ({min(discreteScores)} being worst, {max(discreteScores)} being best)': predicted_scores})

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
        resultEvaluation(subjects, predicted_scores, excelFile)


if __name__=="__main__":
    main()