How to perform fuzzy matches on Odyssey:

Load the Anaconda Python module:

    module load Anaconda

Use conda to install the required packages:

    conda env create -f environment.yml

Activate the environment created above:

    source activate dedupe

Train a gazetteer:

    python train.py --clean-path foreclosures/deduped_banks.csv --messy-path foreclosures/batch1.csv --training-file foreclosures/training_long.json --fields-file foreclosures/fields.json --settings-file foreclosures/my.settings
