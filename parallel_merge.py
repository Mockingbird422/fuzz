'''
The purpose of this script is to make it easy to move around a long
text file without reading the whole file every time. This is important
for parallel IO.
'''
import logging
import math
import sys
import json


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
    

if __name__ == '__main__':
    path = sys.argv[1]
    f = CsvFile(path)
    f.index(4)
    f.print_index()
