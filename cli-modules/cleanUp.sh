#!/usr/bin/bash

for i in */;
do
    rm $i*.npy;
    rm $i*.txt;
    rm $i*reg*.nii.gz;
    rm $i*-fore-mask.nii.gz;

done

