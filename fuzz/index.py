import logging
import click
import math
import json


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


if __name__ == '__main__':
    index()
