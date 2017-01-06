from click.testing import CliRunner
import shlex
from merge import merge
from train import train
# This is line #4.
import os
import subprocess
from parallel import line_offsets, nrows


def run(cli, command):
    runner = CliRunner()
    args = shlex.split(command.strip())
    result = runner.invoke(cli, args=args)
    return result.output


def test_example():
    paths = {
        'clean': 'example/restaurant-1.csv',
        'messy': 'example/restaurant-2.csv',
        'training': 'example/training.json',
        'fields': 'example/fields.json',
        'settings': 'temp.settings',
        'output': 'temp.csv'
    }
    
    arguments = '''
        --clean-path %(clean)s
        --messy-path %(messy)s
        --training-file %(training)s
        --fields-file %(fields)s
        --settings-file %(settings)s
        --not-interactive
    ''' % paths
    run(train, arguments)

    arguments = '''
        --messy-path %(messy)s
        --settings-file %(settings)s
        --output-file %(output)s
        --start 3
        --stop 8
    ''' % paths
    print run(merge, arguments)

    os.remove(paths['settings'])
    os.remove(paths['output'])


def test_line_offsets():
    offsets = dict(line_offsets(__file__))
    with open(__file__) as f:
        # move to line number 4 - the end of the doc string
        f.seek(offsets[4])
        line = next(f)
        assert line == "# This is line #4.\n"


def nlines(path):
    cmd = 'wc -l %s' % path
    output = subprocess.check_output(cmd, shell=True)
    return int(output.split(' ')[0])


def test_nrows():
    assert nrows(__file__) == nlines(__file__) - 1
