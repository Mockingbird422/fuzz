from click.testing import CliRunner
# This is the second line of the file.
import shlex
from merge import merge
from train import train
import os
import subprocess
from parallel_merge import line_offsets, nrows


FILE = __file__[:-1] if __file__.endswith('.pyc') else __file__


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
        --first-row-number 2
        --offset 119
        --nrows 2
    ''' % paths
    print run(merge, arguments)

    os.remove(paths['settings'])
    os.remove(paths['output'])


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
