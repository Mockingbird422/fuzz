#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import viewitems

import itertools
import csv
import exampleIO
import dedupe
import os
import time
import optparse
import logging
import pandas as pd
import numpy as np


def set_logging_level():
    optp = optparse.OptionParser()
    optp.add_option(
        '-v', '--verbose', dest='verbose', action='count',
        help='Increase verbosity (specify multiple times for more)'
    )
    (opts, args) = optp.parse_args()
    log_level = logging.WARNING
    if opts.verbose:
        if opts.verbose == 1:
            log_level = logging.INFO
        elif opts.verbose >= 2:
            log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)


def data_frame_to_dict(data, name):
    return {
        '%s:%d' % (name, i): row.to_dict() for i, row in data.iterrows()
    }


training_file = 'training.json'
clean_path = 'restaurant-1.csv'
messy_path = 'restaurant-2.csv'

set_logging_level()

clean = pd.read_csv(clean_path)
data_1 = data_frame_to_dict(clean, name=clean_path)
messy = pd.read_csv(messy_path)
data_2 = data_frame_to_dict(messy, name=messy_path)

true_matches = clean.set_index('unique_id').join(
    messy.set_index('unique_id'),
    how='inner', lsuffix='_clean', rsuffix='_messy'
)

fields = [
    {'field': 'name', 'type': 'String'},
    {'field': 'address', 'type': 'String'},
    {'field': 'cuisine', 'type': 'String'},
    {'field': 'city', 'type': 'String'}
]

gazetteer = dedupe.Gazetteer(fields)
gazetteer.sample(data_1, data_2, 10000)

# Let's train manually at the console:
if os.path.exists(training_file):
    with open(training_file, 'r') as tf:
        gazetteer.readTraining(tf)
dedupe.consoleLabel(gazetteer)
# Save the manual entries in case we need them later
with open(training_file, 'w') as tf:
    gazetteer.writeTraining(tf)

gazetteer.train()

gazetteer.index(data_1)

alpha = gazetteer.threshold(data_2)

# Add columns to messy data
messy['match_id'] = np.nan
messy['match_probability'] = np.nan
for i, row in messy.iterrows():
    d = row.to_dict()
    match = gazetteer.match({i: d}, threshold=alpha)
    if match:
        pair, phat = match[0][0]
        messy.loc[i, 'match_id'] = pair[1]
        messy.loc[i, 'match_probability'] = phat

print(messy.head())
