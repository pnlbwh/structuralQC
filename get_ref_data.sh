#!/usr/bin/env bash

# get version info
IFS=" = ", read -r _ v < _version.py
__version__=`echo $v | xargs`

echo Downloading reference data
REFDATA=ref_data
wget reference_data/ https://github.com/pnlbwh/structuralQC/releases/download/v${__version__}/$REFDATA.zip
tar -xzvf $REFDATA.zip

# get script directory
SCRIPT=$(readlink -m $(type -p $0))
SCRIPTDIR=$(dirname $SCRIPT)

# define train directory
TRAINDIR=$SCRIPTDIR/$REFDATA

echo Updating config.ini
sed -i "s+train_data+$TRAINDIR+g" $SCRIPTDIR/cli-modules/config.ini
