# SimpleCorrector
Simple Script in Python that looks for simple errors in .tex files in a folder (and sub-folders).


# Implemented Rules

## Rule 1: article 'a' followed by a word starting with a vowel
Example: "a objective"

## Rule 2: article 'an' followed by a consonant
Example: "an variable"

## Rule 3: Repeated words (articles for now)
Example: "the the house"

## Rule 4: Misplaced punctuation/space
Example: 'the car is red .'

# How to use it
python check_errors.py -p 'PATH'

Where PATH is the folder of your TEX project. The script will look for .tex files at the folder and its sub-folders.

For more options try 'python check_errors.py -h', to obtain the help explanation of each command
```
usage: check_errors.py [-h] [-p PATH] [--process_ignored_environments]
                       [-e EXTENSION] [-w [WORDS [WORDS ...]]]

Checks errors in TEX files that are not catch by spell checkers. Example: "an
car", "the the house", "a orange", etc. Errors found are marked with brackets
[], for instance: a[n c]ar, [a o]range.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  By default the script runs in the current folder, use
                        -p "PATH" to indicate the path or file to be checked.
  --process_ignored_environments
                        By default it does not process what is inside of some
                        environmentsthat starts with \begin{...\}. Ignored
                        envs: ['align', 'equation', 'multline', 'tabular']
  -e EXTENSION, --extension EXTENSION
                        Files extension to be searched on the folders
  -w [WORDS [WORDS ...]], --words [WORDS [WORDS ...]]
                        Search for words and expressions in the document.
                        Example: -w Lagrange "a NLP"
```