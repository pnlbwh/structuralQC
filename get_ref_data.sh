#!/usr/bin/env bash

VERSION=2.0.0

# download data
REFDATA=reference_data
wget reference_data/ https://github.com/pnlbwh/structuralQC/archive/v${VERSION}/$REFDATA.zip
tar -xzvf $REFDATA

# get script directory
SCRIPT=$(readlink -m $(type -p $0))
SCRIPTDIR=$(dirname $SCRIPT)

# define train directory
TRAINDIR=$SCRIPTDIR/train_data
mkdir $TRAINDIR

# update config.ini
sed -i "s/train_data/$TRAINDIR/g" $SCRIPTDIR/cli-modules/config.ini
