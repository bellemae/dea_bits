#!/bin/bash

#PBS -P u46
#PBS -q normal
#PBS -l walltime=12:00:00
#PBS -l mem=4GB
#PBS -l ncpus=16
#PBS -l wd

module load dea
module load parallel

LOGDIR="/g/data/u46/users/bt2744/work/data/wofs/log/parallel-save"

# load tile list
TILEFILE="/g/data/u46/users/bt2744/work/data/wofs/config/all-tile-list"
CONFIG="/g/data/u46/users/bt2744/work/code/datacube-stats/configurations/wofs/seasonal_stats_wet.yaml"

echo "tilefile: ${TILEFILE:-tiles}"


# NEED TO MANAGE MULTIPLE NODES, CURRENTLY JUST UP TO 16CPU
# NNODES=$(cat $PBS_NODEFILE | uniq | wc -l)

# split into chunks based on #cpus
NCPUS=$(cat $PBS_NODEFILE | grep $(hostname) | wc -l)
JOBDIR=$PWD
NTILES=$(cat $TILEFILE | wc -l)

#NSPLIT=$(( ($NTILES + $TMPNODES - 1)/$TMPNODES ))
NSPLIT=$(( ($NTILES + $NCPUS - 1) / $NCPUS))

echo "Splitting $NTILES tiles into $NSPLIT chunks"

sort -r -n $TILEFILE | split -d -l $NSPLIT - $JOBDIR/tiles

echo "About to run parallel... "

# call datacube-stats --save-tasks for each chunk of tiles
ls $JOBDIR/tiles* | parallel --delay 5 --retries 3 --load 100% --joblog $LOGDIR \
datacube-stats -vvv --save-tasks {1}tasks.pickle --tile-index-file {1} $CONFIG
