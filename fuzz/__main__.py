import click
# subcommands
from train import train
from merge import main
from index import index
from merge_block import merge_block
from combine import combine
from parallel_merge import parallel_merge

cli = click.Group(commands={
    'train': train,
    'merge': main,
    '_index': index,
    '_merge_block': merge_block,
    '_combine': combine,
    'parallel_merge': parallel_merge,
})

if __name__ == '__main__':
    cli()
