'''
The purpose of this script is to make it easy to move around a long
text file without reading the whole file every time. This is important
for parallel IO.
'''
import logging
import math
import sys


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

    def blocks(self, n):
        '''
        Create `n` blocks of a csv file. Each block (except the last) has
        ceiling(nrows / n) rows.
        '''
        block_size = int(math.ceil(float(self.nrows) / float(n)))

        template = '%(csv_path)s has %(number_of_rows)s rows. To break it into %(n)s blocks, each block will have %(block_size)s rows.'
        data = self.to_dict()
        data.update(locals())
        logging.warn(template % data)

        first_row_in_block = None
        for row, offset in line_offsets(self.path):
            if row % block_size == 1:
                if first_row_in_block is not None:
                    assert row - first_row_in_block == block_size
                first_row_in_block = row
                print {'first_row_number': row, 'offset': offset}
    

if __name__ == '__main__':
    path = sys.argv[1]
    f = CsvFile(path)
    f.blocks(4)
