# fuzz

[![Build Status](https://travis-ci.org/amarder/fuzz.svg?branch=master)](https://travis-ci.org/amarder/fuzz)
[![Coverage Status](https://coveralls.io/repos/github/amarder/fuzz/badge.svg?branch=master)](https://coveralls.io/github/amarder/fuzz?branch=master)

`fuzz` is a Python library designed to make fuzzy merges of large CSV files easy. Why not use [csvdedupe](https://github.com/datamade/csvdedupe)?

*   Support for parallel computation via [Slurm](https://slurm.schedmd.com/). This is convenient if you're working on Harvard's [Odyssey](https://rc.fas.harvard.edu/odyssey/) cluster.

*   Clear separation of the training and merge steps. Use the `train` command to fit your model. Use the `merge` command to merge your two datasets using a previously fitted model. This is helpful if training takes a long time.

# Installation

Load the Anaconda Python module:

    module load Anaconda

Use conda to install the required packages:

    conda env create -f environment.yml

# Usage

Load the Anaconda Python module:

    module load Anaconda

Activate the environment created above:

    source activate dedupe

Train a gazetteer:

    python train.py --clean-path foreclosures/deduped_banks.csv --messy-path batch.csv --training-file training.json --fields-file foreclosures/fields.json --settings-file foreclosures/my.settings

Merge the two datasets:

    python merge.py --messy-path foreclosures/full_data.csv --settings-file foreclosures/my.settings --output-file temp.csv

# Constructing Random Subsample

    head -n 1 foreclosures/full_data.csv > batch.csv
    tail -n +2 foreclosures/full_data.csv | shuf -n 10000 >> batch.csv

# TODO

Evaluating the Merge:

1.  How confident are we that we found _a_ match for each observation? Plot histogram of predicted probabilities over all observations in the messy data.
2.  How confident are we that we found _the_ match for one observation? Plot histogram of predicted probabilities over all observations in the clean data.

As an alternative to using row numbers in the output file we should also allow for specifying id columns.
