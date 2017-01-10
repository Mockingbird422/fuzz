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


def line_offsets(path):
    offset = 0
    with open(path) as f:
        for i, line in enumerate(f):
            yield i, offset
            offset += len(line)


def nrows(csv_path):
    with open(csv_path) as f:
        for i, line in enumerate(f):
            pass
    return i


class CsvFile(object):

    def __init__(self, path):
        self.path = path
        self.nrows = nrows(path)

    def to_dict(self):
        return {
            'csv_path': self.path,
            'number_of_rows': self.nrows,            
        }

    def index(self, nblocks):
        '''
        Create `nblocks` of a csv file. Each block (except the last) has
        ceiling(nrows / nblocks) rows.
        '''
        self.blocks = {}
        block_size = int(math.ceil(float(self.nrows) / float(nblocks)))
        self.block_size = block_size

        template = '%(csv_path)s has %(number_of_rows)s rows. To break it into %(nblocks)s blocks, each block will have %(block_size)s rows.'
        data = self.to_dict()
        data.update(locals())
        logging.info(template % data)

        first_row_in_block = None
        block_number = 1
        for row, offset in line_offsets(self.path):
            if row % block_size == 1:
                if first_row_in_block is not None:
                    assert row - first_row_in_block == block_size
                first_row_in_block = row
                self.blocks[block_number] = {
                    'first_row_number': row,
                    'offset': offset
                }
                block_number += 1

    def print_index(self):
        print json.dumps({
            'path': self.path,
            'nrows': self.nrows,
            'blocks': self.blocks,
            'block_size': self.block_size,
        }, indent=2)


def _combine(inputs, output):
    with open(output, 'w') as outfile:
        for i, path in enumerate(inputs):
            with open(path) as infile:
                for j, line in enumerate(infile):
                    if j == 0:
                        if i == 0:
                            outfile.write(line)
                    else:
                        outfile.write(line)


@click.command()
@click.option('--messy', default='example/restaurant-2.csv')
@click.option('--settings', default='example/my.settings')
@click.option('--nblocks', default=10)
@click.option('--output', default='example/output.csv')
@click.option('--logger-level', default='WARNING')
def parallel_merge(messy, settings, nblocks, output, logger_level):
    csv_file = CsvFile(messy)
    csv_file.index(nblocks)
    cmd_template = '''
        python merge.py \
            --messy-path %(messy)s \
            --logger-level %(logger_level)s \
            --settings-file %(settings)s \
            --output-file %(block_id)d.csv \
            --first-row-number %(first_row_number)d \
            --offset %(offset)d \
            --nrows %(block_size)d
    '''
    for block_id, d in csv_file.blocks.items():
        d.update(locals())
        d['block_size'] = csv_file.block_size
        cmd = cmd_template % d
        subprocess.call(cmd, shell=True)

    # combine the blocks
    paths = ['%d.csv' % (i + 1) for i in range(nblocks)]
    _combine(paths, output)
    for path in paths:
        os.remove(path)


if __name__ == '__main__':
    parallel_merge()
