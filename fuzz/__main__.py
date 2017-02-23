import click
# subcommands
from train import train
from merge import main
from parallel_merge import parallel_merge

cli = click.Group(commands={
    'train': train,
    'merge': main,
    'parallel_merge': parallel_merge,
})

if __name__ == '__main__':
    cli()
