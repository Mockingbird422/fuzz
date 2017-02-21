from click.testing import CliRunner
# This is the second line of the file.
import shlex
from merge import main as merge
from train import train
import os
import subprocess
from index import line_offsets, nrows
from parallel_merge import parallel_merge


FILE = __file__[:-1] if __file__.endswith('.pyc') else __file__


def run(cli, command):
    runner = CliRunner()
    args = shlex.split(command.strip())
    result = runner.invoke(cli, args=args)
    return result.output


def test_example(clean = True):
    paths = {
        'clean': 'example/restaurant-1.csv',
        'messy': 'example/restaurant-2.csv',
        'training': 'example/training.json',
        'fields': 'example/fields.json',
        'settings': 'temp.settings',
        'output': 'temp.csv',
        'output2': 'temp2.csv',
    }

    #######################
    # Train the gazetteer #
    #######################
    arguments = '''
        --clean-path %(clean)s
        --messy-path %(messy)s
        --training-file %(training)s
        --fields-file %(fields)s
        --settings-file %(settings)s
        --not-interactive
    ''' % paths
    run(train, arguments)

    ########################
    # Perform serial merge #
    ########################
    arguments = '''
        --messy-path %(messy)s
        --settings-file %(settings)s
        --output-file %(output)s
    ''' % paths
    run(merge, arguments)
    assert os.path.exists(paths['output'])

    ##########################
    # Perform parallel merge #
    ##########################

    # TODO: How to run without SLURM
    
    # arguments = '''
    #     --messy %(messy)s
    #     --settings %(settings)s
    #     --nblocks 3
    #     --output %(output2)s
    # ''' % paths
    # run(parallel_merge, arguments)

    # serial = open(paths['output']).read()
    # parallel = open(paths['output2']).read()
    # assert serial == parallel

    # os.remove(paths['settings'])
    # os.remove(paths['output'])
    # os.remove(paths['output2'])


def test_line_offsets():
    offsets = dict(line_offsets(FILE))
    with open(FILE) as f:
        f.seek(offsets[1])
        line = next(f)
        assert line == "# This is the second line of the file.\n"


def nlines(path):
    cmd = 'wc -l %s' % path
    output = subprocess.check_output(cmd, shell=True)
    return int(output.split(' ')[0])


def test_nrows():
    number_of_rows = nrows(FILE)
    number_of_lines = nlines(FILE)
    assert number_of_rows == number_of_lines - 1, locals()
