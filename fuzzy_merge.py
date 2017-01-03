#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools
import csv
import dedupe
import os
import time
import optparse
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm
import click
import json
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


def read(path, encoding='utf-8'):
    data_d = {}
 
    with open(path) as f:
        reader = csv.DictReader(f)
        for i, row in tqdm(enumerate(reader)):
            clean_row = {k : _clean(v.decode(encoding)) for (k, v) in row.iteritems()}
            data_d[i] = clean_row

    return data_d


@click.command()
@click.option('--clean-path', default='example/restaurant-1.csv')
@click.option('--messy-path', default='example/restaurant-2.csv')
@click.option('--training-file', default='example/training.json')
@click.option('--logger-level', default='WARNING')
@click.option('--num-cores', default=1)
@click.option('--fields-file', default='example/fields.json')
@click.option('--output-file', default='example/output.csv')
@click.option('--sample-size', default=10000)
def main(clean_path, messy_path, training_file, logger_level, num_cores, fields_file, output_file, sample_size):
    # Set logger level
    log_level = getattr(logging, logger_level)
    logging.getLogger().setLevel(log_level)

    logging.warning('Reading data ...')
    clean = read(clean_path)
    messy = read(messy_path, encoding='latin-1')

    logging.warning('Reading metadata ...')
    with open(fields_file) as f:
        fields = json.load(f)

    logging.warning('Initializing gazetteer ...')
    gazetteer = dedupe.Gazetteer(fields, num_cores=num_cores)

    logging.warning('Sampling pairs for gazetteer ...')
    gazetteer.sample(clean, messy, sample_size=sample_size)

    # Train the gazetteer at the console
    if os.path.exists(training_file):
        with open(training_file, 'r') as tf:
            gazetteer.readTraining(tf)
    dedupe.consoleLabel(gazetteer)
    # Save the manual entries
    with open(training_file, 'w') as tf:
        gazetteer.writeTraining(tf)

    logging.warning('Training gazetteer ...')
    gazetteer.train()

    logging.warning('Indexing gazetteer ...')
    gazetteer.index(clean)

    logging.warning('Find matches ...')
    matches = gazetteer.match(messy, threshold=0)

    logging.warning('Write matches to file ...')
    with open(output_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['messy_id', 'clean_id', 'match_probability'])
        for match in matches:
            pair, phat = match[0]
            csv_writer.writerow([pair[0], pair[1], phat])


if __name__ == '__main__':
    main()
