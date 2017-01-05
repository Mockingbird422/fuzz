from tqdm import tqdm
import click
import csv
import dedupe
import json
import logging
import os
import re


# https://github.com/datamade/dedupe/blob/master/tests/exampleIO.py#L5-L11
def _clean(s):
    result = re.sub('\n', ' ', s)
    result = re.sub(r'[^\x00-\x7F]','?', result) # remove non-ascii characters
    result = re.sub('  +', ' ', result)
    result = result.strip().strip('"').strip("'").lower()
    if not result:
        result = None
    return result


def iter_rows(path, encoding='utf-8'):
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k : _clean(v.decode(encoding)) for (k, v) in row.iteritems()}
            yield clean_row


def read(*args, **kwargs):
    rows = iter_rows(*args, **kwargs)
    return {i: row for i, row in tqdm(enumerate(rows))}


@click.command()
@click.option('--clean-path', default='example/restaurant-1.csv')
@click.option('--messy-path', default='example/restaurant-2.csv')
@click.option('--training-file', default='example/training.json')
@click.option('--logger-level', default='WARNING')
# TODO: If we use Anaconda then multiprocessing will not work because
# Anaconda uses MKL: https://github.com/datamade/dedupe/issues/499
@click.option('--num-cores', default=1)
@click.option('--fields-file', default='example/fields.json')
@click.option('--sample-size', default=10000)
@click.option('--settings-file', default='example/my.settings')
@click.option('--interactive/--not-interactive', default=True)
def main(clean_path, messy_path, training_file, logger_level, num_cores, fields_file, sample_size, settings_file, interactive):
    # Set logger level
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)

    logging.info('Reading data ...')
    clean = read(clean_path)
    messy = read(messy_path, encoding='latin-1')

    logging.info('Reading metadata ...')
    with open(fields_file) as f:
        fields = json.load(f)

    logging.info('Initializing gazetteer ...')
    gazetteer = dedupe.Gazetteer(fields, num_cores=num_cores)

    logging.info('Sampling pairs for gazetteer ...')
    gazetteer.sample(clean, messy, sample_size=sample_size)

    # Train the gazetteer at the console
    if os.path.exists(training_file):
        with open(training_file, 'r') as tf:
            gazetteer.readTraining(tf)

    if interactive:
        dedupe.consoleLabel(gazetteer)
        # Save the manual entries
        with open(training_file, 'w') as tf:
            gazetteer.writeTraining(tf)

    logging.info('Training gazetteer ...')
    gazetteer.train(recall=1.0, index_predicates=False)

    logging.info('Indexing gazetteer ...')
    gazetteer.index(clean)

    with open(settings_file, 'wb') as f:
        gazetteer.writeSettings(f, index=True)


if __name__ == '__main__':
    main()
