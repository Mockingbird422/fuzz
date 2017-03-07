from .functions import merge
import click
import json
import logging
import math
import os


def nrows(csv_path):
    with open(csv_path) as f:
        for i, line in enumerate(f):
            pass
    return i


def line_offsets(path):
    offset = 0
    with open(path) as f:
        for i, line in enumerate(f):
            yield i, offset
            offset += len(line)


class CsvFile(dict):

    def index(self, path, nblocks):
        '''
        Create `nblocks` of a csv file. Each block (except the last) has
        ceiling(nrows / nblocks) rows.
        '''
        self['path'] = path
        self['nrows'] = nrows(path)
        self['nblocks'] = nblocks
        self['blocks'] = {}
        self['block_size'] = int(math.ceil(float(self['nrows']) / float(nblocks)))

        template = '%(path)s has %(nrows)s rows. To break it into %(nblocks)s blocks, each block will have %(block_size)s rows.'
        logging.info(template % self)

        first_row_in_block = None
        block_number = 1
        for row, offset in line_offsets(self['path']):
            if row % self['block_size'] == 1:
                if first_row_in_block is not None:
                    assert row - first_row_in_block == self['block_size']
                first_row_in_block = row
                self['blocks'][block_number] = {
                    'first_row_number': row,
                    'offset': offset
                }
                block_number += 1

    def dump(self, fp):
        json.dump(self, fp=fp, indent=2)

    def load(self, fp):
        data = json.load(fp)
        self.update(data)


@click.command()
@click.option('--messy', default='example/restaurant-2.csv')
@click.option('--nblocks', default=10)
@click.option('--json-file', default='example/index.json')
def index(messy, nblocks, json_file):
    csv_file = CsvFile()
    csv_file.index(path=messy, nblocks=nblocks)
    with open(json_file, 'w') as f:
        csv_file.dump(f)


@click.command()
@click.option('--settings', default='example/my.settings')
@click.option('--json-file', default='example/index.json')
@click.option('--block-id', default=1)
def merge_block(settings, json_file, block_id):
    csv_file = CsvFile()
    with open(json_file) as f:
        csv_file.load(f)

    block = csv_file['blocks'][str(block_id)]

    kwargs = {
        'messy_path': csv_file['path'],
        'settings_file': settings,
        'output_file': '%d.csv' % block_id,
        'first_row_number': block['first_row_number'],
        'offset': block['offset'],
        'nrows': csv_file['block_size'],
    }
    merge(**kwargs)


@click.command()
@click.option('--json-file', default='example/index.json')
@click.option('--output', default='output.csv')
def combine(json_file, output):
    csv_file = CsvFile()
    with open(json_file) as f:
        csv_file.load(f)
    with open(output, 'w') as outfile:
        for i in range(1, csv_file['nblocks'] + 1):
            path = '%d.csv' % i
            with open(path) as infile:
                for j, line in enumerate(infile):
                    if j == 0:
                        if i == 1:
                            outfile.write(line)
                    else:
                        outfile.write(line)

    # clean up
    for i in range(1, csv_file['nblocks'] + 1):
        path = '%d.csv' % i
        os.remove(path)
    os.remove(json_file)
