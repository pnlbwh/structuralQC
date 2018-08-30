#!/bin/bash

antsRegistration \
-d 3 \
-r [$imgs, 1] \
-m mattes[$imgs, 1, 32, regular, 0.1] \
-t affine[0.1] \
-c [500x500x50, 1e-3, 20] \
-s 4x2x1vox \
-n bspline \
-f 3x2x1 \
-l 1 \
-z 1 \
-o [$op, ${op}-reg.nii.gz]

rm ${op}0GenericAffine.mat
mv ${op}-reg.nii.gz directory/
