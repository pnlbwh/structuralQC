#!/usr/bin/env python

import configparser
import os, sys
import pandas as pd
import multiprocessing
import ast

from loadFile import loadExcel
from calculation import processImage
from errorChecking import errorChecking, globCheck

from sklearn.metrics import confusion_matrix

SCRIPTDIR= os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(SCRIPTDIR, 'config.ini'))
discreteScores = ast.literal_eval(config['TRAINING']['discreteScores'])
excelFile= config['TRAINING']['visual_qc_excel_file']
N_CPU= int(config['RESOURCE']['N_CPU'])

def resultEvaluation(caselistSubjects, predicted_scores, modality, outDir):

    # read the Subject ID and {modality} column
    excelCaseIds, visual_scores= loadExcel(excelFile, modality)

    true_scores= [visual_scores[excelCaseIds.index(s)] for s in caselistSubjects]


    orig_stdout = sys.stdout
    f = open(os.path.join(outDir, 'confusion_matrix.txt'), 'w')
    sys.stdout = f

    # reshaping and data type consistency are required
    print("Confusion matrix (columns are true labels, rows are predicted labels):")
    print("Visual discrete scores are: ", discreteScores)
    print(confusion_matrix(true_scores, predicted_scores, labels= discreteScores))

    sys.stdout = orig_stdout


def batchProcessing(imgs, subjects, modality, outDir):

    num_sub = len(subjects)

    # Use all available cores, otherwise specify the number you want as an argument
    pool = multiprocessing.Pool(N_CPU)
    res=[]
    for img in imgs:
        res.append(pool.apply_async(func= processImage, args= (img, '', modality)))

    predicted_scores=[]
    predicted_quality=[]
    for r in res:
        attributes  = r.get()
        predicted_scores.append(attributes[0])
        predicted_quality.append(attributes[1])

    pool.close()
    pool.join()


    df= pd.DataFrame({'Case #': subjects,
            f'Predicted score ({min(discreteScores)} being worst, {max(discreteScores)} being best)': predicted_scores,
            'Quality': predicted_quality})

    df.to_csv(os.path.join(outDir, f'{modality}_QC_scores.csv'), index= False)

    if excelFile!='None':
        resultEvaluation(subjects, predicted_scores, modality, outDir)

def main():
    pass
    # run test qc on a small set of images


if __name__=="__main__":
    main()
