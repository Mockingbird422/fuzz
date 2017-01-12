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

    def write_index(self, path):
        with open(path, 'w') as f:
            json.dump({
                'path': self.path,
                'nrows': self.nrows,
                'blocks': self.blocks,
                'block_size': self.block_size,
            }, fp=f, indent=2)


@click.command()
@click.option('--messy', default='example/restaurant-2.csv')
@click.option('--nblocks', default=10)
@click.option('--json-file', default='index.json')
def index(messy, nblocks, json_file):
    csv_file = CsvFile(messy)
    csv_file.index(nblocks)
    csv_file.write_index(json_file)


if __name__ == '__main__':
    index()
