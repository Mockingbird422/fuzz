#!/bin/bash
#
#SBATCH -p hbs_rcs          # Partition
#SBATCH -n 1                # one core
#SBATCH -N 1                # on one node
#SBATCH -t 7-00:00          # Running time of 7 days
#SBATCH --mem 4000          # Memory request of 4 GB
#SBATCH --open-mode=append  # Don't reset log when requeued
#SBATCH --constraint=holyib # run on InfiniBand

echo "$*"
merge_block --block-id ${SLURM_ARRAY_TASK_ID} $*
