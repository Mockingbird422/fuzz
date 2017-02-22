from tqdm import tqdm
from train import read_csv, data_path
import click
import csv
import dedupe
import logging
import os


def merge(messy_path, settings_file, output_file, first_row_number,
          offset, nrows):
    # Set logger level
    log_level = os.environ.get('LOGGER_LEVEL', 'WARNING')
    logging.getLogger().setLevel(log_level)

    logging.info('Initializing gazetteer ...')
    with open(settings_file) as f:
        gazetteer = dedupe.StaticGazetteer(f, num_cores=1)

    rows = read_csv(
        messy_path,
        first_row_number=first_row_number,
        offset=offset,
        nrows=nrows,
        encoding='latin-1'
    )

    with open(output_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['messy_row', 'clean_row', 'match_probability'])
        for i, row in tqdm(rows):
            try:
                matches = gazetteer.match({i: row}, threshold=0)
            except ValueError:
                matches = []
            assert len(matches) in [0, 1]
            if len(matches) == 0:
                out_row = [i, '', 0]
            else:
                match = matches[0]
                pair, phat = match[0]
                out_row = [i, pair[1], phat]
            csv_writer.writerow(out_row)
            if i % 100 == 0:
                f.flush()


@click.command()
@click.option('--messy-path', default=data_path('restaurant-2.csv'))
@click.option('--settings-file', default='my.settings')
@click.option('--output-file', default='output.csv')
@click.option('--first-row-number', default=None, type=int)
@click.option('--offset', default=None, type=int)
@click.option('--nrows', default=None, type=int)
def main(*args, **kwargs):
    merge(*args, **kwargs)


if __name__ == '__main__':
    main()
