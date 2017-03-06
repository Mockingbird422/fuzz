from .functions import merge
from .index import CsvFile
import click


@click.command()
@click.option('--settings', default='example/my.settings')
@click.option('--json-file', default='example/index.json')
@click.option('--block-id', default=1)
def merge_block(settings, json_file, block_id):
    csv_file = CsvFile()
    with open(json_file) as f:
        csv_file.load(f)

    block = csv_file['blocks'][str(block_id)]

    kwargs = {
        'messy_path': csv_file['path'],
        'settings_file': settings,
        'output_file': '%d.csv' % block_id,
        'first_row_number': block['first_row_number'],
        'offset': block['offset'],
        'nrows': csv_file['block_size'],
    }
    merge(**kwargs)


if __name__ == '__main__':
    merge_block()
