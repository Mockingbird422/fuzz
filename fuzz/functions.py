'''
Functions for performing fuzzy merges.
'''

from __future__ import print_function
from __future__ import unicode_literals
from tqdm import tqdm
import csv
import dedupe
import json
import logging
import os
import pkg_resources
import re
import subprocess
import time


def _set_logger_level():
    log_level = os.environ.get('LOGGER_LEVEL', 'WARNING')
    logging.getLogger().setLevel(log_level)


def get_path(*args):
    relpath = os.path.join(*args)
    return pkg_resources.resource_filename('fuzz', relpath)


############
# Training #
############


# https://github.com/datamade/dedupe/blob/master/tests/exampleIO.py#L5-L11
def _clean(s):
    result = re.sub('\n', ' ', s)
    # remove non-ascii characters
    result = re.sub(r'[^\x00-\x7F]', '?', result)
    result = re.sub('  +', ' ', result)
    result = result.strip().strip('"').strip("'").lower()
    if not result:
        result = None
    return result


def read_csv(path, first_row_number=None, offset=None, nrows=None,
             encoding='utf-8'):
    assert (
        first_row_number is None and
        offset is None and
        nrows is None
    ) or (
        first_row_number is not None and
        offset is not None and
        nrows is not None
    )

    read_whole_file = first_row_number is None

    clean_row = lambda x: {
        k: _clean(v)
        for (k, v) in
        x.items()
        if k is not None  # remove entries that have no header
    }

    with open(path) as f:
        reader = csv.DictReader(f)

        if read_whole_file:
            for i, row in enumerate(reader):
                yield i + 1, clean_row(row)
        else:
            next(reader)   # initialize the headers
            f.seek(offset)  # reposition the reader
            for i, row in enumerate(reader):
                yield first_row_number + i, clean_row(row)
                if i == nrows - 1:
                    break


def read(*args, **kwargs):
    enum_rows = read_csv(*args, **kwargs)
    return {i: row for i, row in enum_rows}


def train(clean_path, messy_path, fields_file,
          training_file='training.json', settings_file='my.settings',
          sample_size=10000, num_cores=1, interactive=False):
    '''
    Train a model to perform a fuzzy merge.
    '''
    _set_logger_level()

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


#########
# Merge #
#########


def merge(messy_path, settings_file, output_file, first_row_number,
          offset, nrows):
    '''
    Perform a fuzzy merge.
    '''
    _set_logger_level()

    logging.info('Initializing gazetteer ...')
    with open(settings_file, 'rb') as f:
        gazetteer = dedupe.StaticGazetteer(f, num_cores=1)

    rows = read_csv(
        messy_path,
        first_row_number=first_row_number,
        offset=offset,
        nrows=nrows,
        encoding='latin-1'
    )

    with open(output_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['messy_row', 'clean_row', 'match_probability'])
        for i, row in tqdm(rows):
            try:
                matches = gazetteer.match({i: row}, threshold=0)
            except ValueError:
                matches = []
            assert len(matches) in [0, 1]
            if len(matches) == 0:
                out_row = [i, '', 0]
            else:
                match = matches[0]
                pair, phat = match[0]
                out_row = [i, pair[1], phat]
            csv_writer.writerow(out_row)
            if i % 100 == 0:
                f.flush()


##################
# Parallel Merge #
##################


def _slurm_available():
    retcode = subprocess.call('which sbatch', shell=True)
    return retcode == 0


class Slurm(object):
    '''
    Use Slurm to merge two CSV files in parallel.
    '''

    INDEX = ' '.join([
        'sbatch',
        get_path('scripts', 'index.sh'),
        '--messy %(messy)s',
        '--nblocks %(nblocks)d',
        '--json-file %(json_file)s'
    ])

    MERGE_BLOCKS = ' '.join([
        'sbatch',
        '--dependency=afterok:%(index_job_id)d',
        '--array=1-%(nblocks)d',
        get_path('scripts', 'merge_block.sh'),
        '--settings %(settings)s',
        '--json-file %(json_file)s'
    ])

    COMBINE = ' '.join([
        'sbatch',
        '--dependency=afterok:%(merge_job_id)d',
        get_path('scripts', 'combine.sh'),
        '--json-file %(json_file)s',
        '--output %(output)s'
    ])

    def _call(self, command):
        print(command)
        output = subprocess.check_output(command, shell=True)
        m = re.search('^Submitted batch job (\d+)$', output)
        assert m, output
        return int(m.group(1))

    def merge(self, messy, settings, nblocks, output, json_file):
        ##############################
        # Index the large messy file #
        ##############################
        command = self.INDEX % locals()
        index_job_id = self._call(command)
        time.sleep(1)

        ####################
        # Merge each block #
        ####################
        command = self.MERGE_BLOCKS % locals()
        merge_job_id = self._call(command)
        time.sleep(1)

        ######################
        # Combine the blocks #
        ######################
        command = self.COMBINE % locals()
        self._call(command)


class Serial(Slurm):
    '''
    Most development machines will not have Slurm set up. Use this
    code to test the parallel merge when Slurm is not available.
    '''

    INDEX = ' '.join([
        get_path('scripts', 'index.sh'),
        '--messy %(messy)s',
        '--nblocks %(nblocks)d',
        '--json-file %(json_file)s'
    ])

    MERGE_BLOCKS = ' '.join([
        get_path('scripts', 'merge_block.sh'),
        '--settings %(settings)s',
        '--json-file %(json_file)s'
    ])

    COMBINE = ' '.join([
        get_path('scripts', 'combine.sh'),
        '--json-file %(json_file)s',
        '--output %(output)s'
    ])

    def _call(self, command):
        print(command)
        output = subprocess.check_output(command, shell=True)
        return output

    def merge(self, messy, settings, nblocks, output, json_file):
        ##############################
        # Index the large messy file #
        ##############################
        command = self.INDEX % locals()
        self._call(command)

        ####################
        # Merge each block #
        ####################
        for i in range(1, nblocks + 1):
            os.environ['SLURM_ARRAY_TASK_ID'] = str(i)
            command = self.MERGE_BLOCKS % locals()
            self._call(command)

        ######################
        # Combine the blocks #
        ######################
        command = self.COMBINE % locals()
        self._call(command)


def parallel_merge(*args, **kwargs):
    '''
    Perform a fuzzy merge in parallel.
    '''
    s = Slurm() if _slurm_available() else Serial()
    s.merge(*args, **kwargs)
