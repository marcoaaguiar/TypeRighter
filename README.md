# SimpleCorrector
Simple Script in Python that looks for simple errors in .tex files in a folder (and subfolders).


# Implemented Rules

## Rule 1: article 'a' followed by a word starting with a vowel
Example: "a objective"

## Rule 2: article 'an' followe by a consonant
Example: "an variable"

## Rule 3: Repeated words (articles for now)
Eaxmple: "the the"

# How to use it
python check_errors.py 'PATH'

Where PATH is the folder of your project. The script will look for .tex files at the folder and its sub-folders.
