#!/bin/SlicerApp-real

BRAINSROIAuto \
--inputVolume $1 \
--outputVolumePixelType uint \
--otsuPercentileThreshold 0.21 \
--thresholdCorrectionFactor 0.7 \
--outputROIMaskVolume $2
