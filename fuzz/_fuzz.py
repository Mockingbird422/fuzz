import click
# subcommands
from .index import index
from .merge_block import merge_block
from .combine import combine

cli = click.Group(commands={
    'index': index,
    'merge_block': merge_block,
    'combine': combine,
})

if __name__ == '__main__':
    cli()
