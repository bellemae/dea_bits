#!/bin/bash


# for each saved task file, submit a pbs job


CONFIG="/g/data/u46/users/bt2744/work/code/datacube-stats/configurations/wofs/seasonal_stats_wet.yaml"
QSUB="project=v10,mem=medium,ncpus=10,walltime=10h,queue=normal,name=wofs-seasonal"
JOBDIR="/g/data/u46/users/bt2744/work/data/wofs"

# call datacube-stats --load-tasks for each pickle file
for i in $( ls $JOBDIR/*tasks.pickle ); do
    TILES=${i%"tasks.pickle"}
    datacube-stats -vvv --qsub=$QSUB --load-tasks $i --tile-index-file $TILES $CONFIG
done;