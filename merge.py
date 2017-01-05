from tqdm import tqdm
from train import iter_rows
import click
import csv
import dedupe
import logging


@click.command()
@click.option('--messy-path', default='example/restaurant-2.csv')
@click.option('--logger-level', default='WARNING')
@click.option('--num-cores', default=1)
@click.option('--settings-file', default='example/my.settings')
@click.option('--output-file', default='example/output.csv')
def merge(messy_path, logger_level, num_cores, settings_file, output_file):
    # Set logger level
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)

    logging.info('Initializing gazetteer ...')
    with open(settings_file) as f:
        gazetteer = dedupe.StaticGazetteer(f, num_cores=num_cores)

    rows = iter_rows(messy_path, encoding='latin-1')

    with open(output_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['messy_id', 'clean_id', 'match_probability'])
        for i, row in tqdm(enumerate(rows)):
            matches = gazetteer.match({i: row}, threshold=0)
            for match in matches:
                pair, phat = match[0]
                csv_writer.writerow([pair[0], pair[1], phat])
                if i % 100:
                    f.flush()


if __name__ == '__main__':
    merge()
