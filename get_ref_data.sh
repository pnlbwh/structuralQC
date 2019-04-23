#!/usr/bin/env bash

VERSION=2.0.4

echo Downloading reference data
REFDATA=ref_data
wget reference_data/ https://github.com/pnlbwh/structuralQC/releases/download/v$VERSION/$REFDATA.zip
tar -xzvf $REFDATA.zip

# get script directory
SCRIPT=$(readlink -m $(type -p $0))
SCRIPTDIR=$(dirname $SCRIPT)

# define train directory
TRAINDIR=$SCRIPTDIR/$REFDATA

echo Updating config.ini
sed -i "s+train_data+$TRAINDIR+g" $SCRIPTDIR/cli-modules/config.ini
