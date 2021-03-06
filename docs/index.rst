fuzz
====

fuzz is a Python package designed to make fuzzy merges of large CSV
files easy.

Motivation
----------

Why use fuzz instead of `csvdedupe <https://github.com/datamade/csvdedupe>`_?

*   fuzz uses less memory.

*   fuzz supports parallel computation via `Slurm
    <https://slurm.schedmd.com/>`_. This is convenient if you're
    working on Harvard's `Odyssey <https://rc.fas.harvard.edu/odyssey/>`_ cluster.

*   fuzz separates the training and merge steps. Use the `train` command to fit your model. Use the `merge` command to merge your two datasets using a previously fitted model. This is helpful if training takes a long time.

Installation
------------

This package can be installed via pip::

    pip install git+https://github.com/amarder/fuzz.git

Getting help
------------

I've tried to include the most important documentation as part of the command line tool so it's easy to get help. To see a list of the available fuzz commands use::

    fuzz --help
    
To get help on a specific command (`train`, `merge`, or `parallel_merge`) use::

    fuzz train --help
    fuzz merge --help
    fuzz parallel_merge --help

A simple example
----------------

fuzz ships with four example files:

1.  **restaurant-1.csv** a CSV file containing 112 restaurant addresses. This is a table of clean data (each row is a unique restaurant).
2.  **restaurant-2.csv** a CSV file containing 752 restaurant addresses. This is a table of messy data (multiple rows may refer to the same restaurant).
3.  **fields.json** a JSON file describing what columns we want to merge by.
4.  **training.json** a JSON file with ten pairs of addresses from the two CSV files that match (after inspecting the two addresses I determined they referred to the same restaurant), and eleven pairs of addresses that don't match (they refer to two different restaurants).

There are two steps involved in using fuzz:

1.  `train` a model that can be used to predict whether two rows refer to the same entity, and
2.  `merge` two CSV files using the fitted model from step 1. If speed is a concern and you're working on a high performance computing cluster with Slurm, consider using `parallel_merge` instead of `merge`.

Let's train a model using the restaurant data (this will create a new
file called `my.settings` that describes the `fitted model <https://dedupe.readthedocs.io/en/latest/API-documentation.html#staticgazetteer-objects>`_)::

    fuzz train

Now let's merge the restaurant data (this will create a new file called `output.csv` that describes the fuzzy matches)::

    fuzz merge

A more realistic example
------------------------

Imagine you have a CSV file describing a bunch of mortgages and a CSV files describing all the banks in the US. Unfortunately, the mortgage data is messy and you want to link each mortgage up to the right bank. Here's how you would train your model::

    fuzz train \
        --clean-path banks.csv \
        --messy-path mortgages.csv \
        --fields-file yourfields.json \
        --training-file yourtraining.json \
        --settings-file your.settings

The training file does not need to exist (you will interactively
construct the training file marking which mortgage-bank pairs match),
but you do need to set up the fields file. For a description of what
needs to be in your fields file see `this page
<http://dedupe.readthedocs.io/en/latest/Variable-definition.html>`_
describing how to define variables for `dedupe <http://dedupe.readthedocs.io/en/latest/index.html>`_. After you have trained your model this will create a new file called `your.settings` that describes the fitted model, now you're ready to merge::

    fuzz merge \
        --settings-file your.settings \
        --messy-path mortgages.csv \
        --output-file yourresults.csv
        
This will create a new file called `yourresults.csv` that has one row for each mortgage. Each row will have the row number associated with the mortgage, the row number associated with the bank that most closely matches the information from that mortgage, and a probability estimate of how confident the model is that this is a correct match.


Odyssey
=======

A big reason why I developed this package was to leverage the computational power on Harvard's Odyssey cluster. This section describes how I would use fuzz on Odyssey. There are many other workflows one could follow. If you run into issues, it might make sense to consult the `Odyssey Quick Start Guide <https://rc.fas.harvard.edu/resources/odyssey-quickstart-guide/>`_ or the `Resources <https://rc.fas.harvard.edu/resources/>`_ page.

Installation
------------

Unfortunately, installing this package on Odyssey is a little harder
than on one's local machine. Here are the steps I used to install it in a virtual environment:

1.  Create a new virtual environment using conda::

        module load Anaconda
        conda create -n myenv python --yes

2.  Activate the environment::

        source activate myenv

3.  Install pip::

        conda install pip --yes

4.  Use pip to install fuzz::

        pip install git+https://github.com/amarder/fuzz.git

Usage
-----

Here's how I would fuzzy merge two CSV files on Odyssey:

1.  Make sure that you've activated your virtual environment::

        which fuzz

2.  Train your model on a back-end node::

        srun --pty --mem 4000 -p hbs_rcs -t 0-8:00 -n 1 -N 1 \
        fuzz train \
            --clean-path banks.csv \
            --messy-path mortgages.csv \
            --fields-file yourfields.json \
            --training-file yourtraining.json \
            --settings-file your.settings

3.  Use the `parallel_merge` command to run your fuzzy merge on back-end nodes::

        fuzz parallel_merge \
            --settings-file your.settings \
            --messy-path mortgages.csv \
            --output-file yourresults.csv

    This command submits three jobs to Slurm: (1) it creates an index
    file describing the large CSV file mortgages.csv, (2) it submits a
    job array so that blocks of the large CSV file can be matched with
    the clean CSV file in parallel, and (3) it combines the merged
    blocks together into a single output file. When you run this
    command you will see the `sbatch` commands it issues to Slurm.


Frequently asked questions
==========================

Constructing a random sample
----------------------------

I've found the following commands useful for extracting a random sample of a large CSV file::

    head -n 1 big.csv > sample.csv
    tail -n +2 big.csv | shuf -n 10000 >> sample.csv

This was particularly useful for training on large files. Note that `shuf` does read the entire file into memory.


API
===

.. automodule:: fuzz.functions
    :members: train, merge, parallel_merge
