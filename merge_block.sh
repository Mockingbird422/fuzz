#!/bin/bash
#
#SBATCH -p serial_requeue # Partition
#SBATCH -n 1              # one core
#SBATCH -N 1              # on one node
#SBATCH -t 0-1:00         # Running time of 1 hour
#SBATCH --mem 4000        # Memory request of 4 GB

echo "$*"
python merge_block.py --block-id ${SLURM_ARRAY_TASK_ID} $*
