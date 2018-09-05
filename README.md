Quality checking algoritm for T1/T2 mri
In the structural MRI directory, use the following to generate caselist.txt `ls >> caselist.txt`
Then, visually delete any irrelevant files/folders in caselist.txt




[TRAINING]

# integer scores
discreteScores = [1,2,3,4]

# xlsx file containing visual qc scores
visual_qc_excel_file= structuralQC/trainingData/visual_qc.xlsx

# fixed reference images
fixedImaget1= structuralQC/trainingData/1001-t1w-xc-reg.nii.gz
fixedImaget2= structuralQC/trainingData/1001-t2w-xc-reg.nii.gz

# training foreground mask folder
# (subfolders are defined according to subjects in the xlsx file)
maskFolder = structuralQC/trainingData/registered_foreground_masks

# training features
t1Histogram = structuralQC/trainingData/patch_histograms_t1.npy
t2Histogram = structuralQC/trainingData/path_histograms_t2.npy
