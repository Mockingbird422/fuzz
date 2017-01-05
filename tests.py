from click.testing import CliRunner
import shlex
from merge import merge
from train import train
import os


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
