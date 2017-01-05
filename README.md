# Fuzzy Merge

How to perform fuzzy matches on Odyssey.

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

# Parallel Processing

I think the simplest way to break this up is to pass start and stop options to the merge. Then I'll have another program that copies files to /n/regal/ and runs a job array and weaves the results back together.

1.  Add start and stop options to merge.

# TODO

How to measure confidence in results?

# Constructing Random Subsample

    head -n 1 foreclosures/full_data.csv > batch.csv
    tail -n +2 foreclosures/full_data.csv | shuf -n 10000 >> batch.csv
