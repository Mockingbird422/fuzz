#!/bin/bash
#
#SBATCH -p serial_requeue  # Partition
#SBATCH -n 1               # one core
#SBATCH -N 1               # on one node
#SBATCH -t 10              # Running time of 10 minutes
#SBATCH --mem 4000         # Memory request of 4 GB
#SBATCH --open-mode=append # Don't reset log when requeued

echo "$*"
python /n/hbs_pilot/Lab/amarder/gazetteer/merge_block.py --block-id ${SLURM_ARRAY_TASK_ID} $*
