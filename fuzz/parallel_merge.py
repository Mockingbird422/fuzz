'''
The purpose of this script is to make it easy to move around a long
text file without reading the whole file every time. This is important
for parallel IO.
'''
import logging
import math
import sys
import json
import click
import subprocess
import os
import re
import time


def my_call(command):
    print command
    output = subprocess.check_output(command, shell=True)
    m = re.search('^Submitted batch job (\d+)$', output)
    assert m, output
    return int(m.group(1))


INDEX = '''
sbatch %(this_directory)s/index.sh --messy %(messy)s --nblocks %(nblocks)d --json-file %(json_file)s
'''

MERGE_BLOCKS = '''
sbatch --dependency=afterok:%(index_job_id)d --array=1-%(nblocks)d \
%(this_directory)s/merge_block.sh --settings %(settings)s --json-file %(json_file)s
'''

COMBINE = '''
sbatch --dependency=afterok:%(merge_job_id)d \
%(this_directory)s/combine.sh --json-file %(json_file)s --output %(output)s
'''


@click.command()
@click.option('--messy', default='example/restaurant-2.csv')
@click.option('--settings', default='example/my.settings')
@click.option('--nblocks', default=10)
@click.option('--output', default='example/output.csv')
@click.option('--json-file', default='temp.json')
def parallel_merge(messy, settings, nblocks, output, json_file):
    this_directory = os.path.dirname(os.path.abspath(__file__))
    
    ##############################
    # Index the large messy file #
    ##############################
    command = INDEX % locals()
    index_job_id = my_call(command)
    time.sleep(1)

    ####################
    # Merge each block #
    ####################
    command = MERGE_BLOCKS % locals()
    merge_job_id = my_call(command)
    time.sleep(1)

    ######################
    # Combine the blocks #
    ######################
    command = COMBINE % locals()
    my_call(command)


if __name__ == '__main__':
    parallel_merge()
