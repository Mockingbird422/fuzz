import click
import os


@click.command()
@click.option('--nblocks', default=10)
@click.option('--output', default='output.csv')
def combine(nblocks, output):
    with open(output, 'w') as outfile:
        for i in range(1, nblocks + 1):
            path = '%d.csv' % i
            with open(path) as infile:
                for j, line in enumerate(infile):
                    if j == 0:
                        if i == 1:
                            outfile.write(line)
                    else:
                        outfile.write(line)
    for i in range(1, nblocks + 1):
        path = '%d.csv' % i
        os.remove(path)


if __name__ == '__main__':
    combine()
