import click
import os
from index import CsvFile


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


if __name__ == '__main__':
    combine()
