from tqdm import tqdm
from train import read
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
def main(messy_path, logger_level, num_cores, settings_file, output_file):
    # Set logger level
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)

    logging.info('Reading data ...')
    messy = read(messy_path, encoding='latin-1')

    logging.info('Initializing gazetteer ...')
    with open(settings_file) as f:
        gazetteer = dedupe.StaticGazetteer(f, num_cores=num_cores)

    logging.info('Find matches ...')
    matches = gazetteer.match(messy, threshold=0)

    logging.info('Write matches to file ...')
    with open(output_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['messy_id', 'clean_id', 'match_probability'])
        for match in matches:
            pair, phat = match[0]
            csv_writer.writerow([pair[0], pair[1], phat])


if __name__ == '__main__':
    main()
