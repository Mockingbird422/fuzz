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


def _data_frame_to_dict(data, name):
    return {
        i: row.to_dict() for i, row in data.iterrows()
    }


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

    # Read data
    clean = pd.read_csv(clean_path)
    messy = pd.read_csv(messy_path)

    # Prepare data for gazetteer
    data_1 = _data_frame_to_dict(clean, name=clean_path)
    data_2 = _data_frame_to_dict(messy, name=messy_path)

    # Read metadata
    with open(fields_file) as f:
        fields = json.load(f)

    # Set up gazetteer
    gazetteer = dedupe.Gazetteer(fields, num_cores=num_cores)
    gazetteer.sample(data_1, data_2, sample_size=sample_size)

    # Train the gazetteer at the console
    if os.path.exists(training_file):
        with open(training_file, 'r') as tf:
            gazetteer.readTraining(tf)
    dedupe.consoleLabel(gazetteer)
    # Save the manual entries
    with open(training_file, 'w') as tf:
        gazetteer.writeTraining(tf)

    gazetteer.train()
    gazetteer.index(data_1)

    # Add columns to messy data
    messy['match_id'] = -1
    messy['match_probability'] = np.nan
    for i, row in tqdm(messy.iterrows()):
        d = row.to_dict()
        match = gazetteer.match({i: d}, threshold=0)
        if match:
            pair, phat = match[0][0]
            messy.loc[i, 'match_id'] = pair[1]
            messy.loc[i, 'match_probability'] = phat

    messy.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()
