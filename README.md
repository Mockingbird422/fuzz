# Fuzzy Merge

How to perform fuzzy matches on Odyssey.

## Installation

Load the Anaconda Python module:

    module load Anaconda

Use conda to install the required packages:

    conda env create -f environment.yml

## Usage

Load the Anaconda Python module:

    module load Anaconda

Activate the environment created above:

    source activate dedupe

Train a gazetteer:

    python train.py --clean-path foreclosures/deduped_banks.csv --messy-path batch.csv --training-file training.json --fields-file foreclosures/fields.json --settings-file foreclosures/my.settings

Merge the two datasets:

    python fuzzy_merge.py --messy-path foreclosures/full_data.csv --settings-file foreclosures/my.settings --output-file temp.csv

## TODO

How to measure confidence in results?

# Constructing Random Subsample

    head -n 1 foreclosures/full_data.csv > batch.csv
    tail -n +2 foreclosures/full_data.csv | shuf -n 10000 >> batch.csv
