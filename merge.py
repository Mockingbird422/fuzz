from tqdm import tqdm
from train import iter_rows
import click
import csv
import dedupe
import logging
import itertools


@click.command()
@click.option('--messy-path', default='example/restaurant-2.csv')
@click.option('--logger-level', default='WARNING')
@click.option('--num-cores', default=1)
@click.option('--settings-file', default='example/my.settings')
@click.option('--output-file', default='example/output.csv')
@click.option('--start', default=None, type=int)
@click.option('--stop', default=None, type=int)
def merge(messy_path, logger_level, num_cores, settings_file, output_file, start, stop):
    # Set logger level
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)

    logging.info('Initializing gazetteer ...')
    with open(settings_file) as f:
        gazetteer = dedupe.StaticGazetteer(f, num_cores=num_cores)

    rows = iter_rows(messy_path, encoding='latin-1')
    enumerated_rows = enumerate(rows)
    selected_rows = itertools.islice(enumerated_rows, start, stop)

    with open(output_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['messy_id', 'clean_id', 'match_probability'])
        for i, row in tqdm(selected_rows):
            matches = gazetteer.match({i: row}, threshold=0)
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


if __name__ == '__main__':
    merge()
