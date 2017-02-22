import click
import subprocess
import os
import re
import time
from train import get_path


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
        print command
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
        print command
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


@click.command()
@click.option('--messy', default=get_path('data', 'restaurant-2.csv'))
@click.option('--settings', default='my.settings')
@click.option('--nblocks', default=10)
@click.option('--output', default='output.csv')
@click.option('--json-file', default='temp.json')
def parallel_merge(*args, **kwargs):
    s = Slurm() if _slurm_available() else Serial()
    s.merge(*args, **kwargs)


if __name__ == '__main__':
    parallel_merge()
