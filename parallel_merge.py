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


def my_call(command):
    print command
    subprocess.call(command, shell=True)


@click.command()
@click.option('--messy', default='example/restaurant-2.csv')
@click.option('--settings', default='example/my.settings')
@click.option('--nblocks', default=10)
@click.option('--output', default='example/output.csv')
def parallel_merge(messy, settings, nblocks, output):
    ##############################
    # Index the large messy file #
    ##############################
    json_file = 'temp.json'
    command = 'python index.py --messy %(messy)s --nblocks %(nblocks)d --json-file %(json_file)s' % locals()
    my_call(command)

    ####################
    # Merge each block #
    ####################
    for i in range(1, nblocks + 1):
        command = 'python merge_block.py --settings %(settings)s --json-file %(json_file)s --block-id %(i)d' % locals()
        my_call(command)

    ######################
    # Combine the blocks #
    ######################
    command = 'python combine.py --nblocks %(nblocks)d --output %(output)s' % locals()
    my_call(command)
    os.remove(json_file)


if __name__ == '__main__':
    parallel_merge()
