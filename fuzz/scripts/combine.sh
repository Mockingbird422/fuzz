#!/bin/bash
#
#SBATCH -p hbs_rcs        # Partition
#SBATCH -n 1              # one core
#SBATCH -N 1              # on one node
#SBATCH -t 0-1:00         # Running time of 1 hour
#SBATCH --mem 4000        # Memory request of 4 GB

combine $*
