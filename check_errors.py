import argparse
import os
import string

PATH = ""

# ==============================================================================
# OPTIONS
# ==============================================================================

IGNORE_MATH_MODE = True

# ==============================================================================
# ALPHABET AND OTHER DEFINITIONS
# ==============================================================================

ALPHABET_LOWERCASE = list(string.ascii_lowercase)
ALPHABET_UPPERCASE = list(string.ascii_uppercase)
ALPHABET = ALPHABET_LOWERCASE + ALPHABET_UPPERCASE

VOWELS_LOWERCASE = 'aeiou'
VOWELS_UPPERCASE = 'AEIOU'
VOWELS = VOWELS_LOWERCASE + VOWELS_UPPERCASE


def is_vowel(letter): return letter in VOWELS


CONSONANTS_LOWERCASE = [letter for letter in ALPHABET_LOWERCASE if not is_vowel(letter)]
CONSONANTS_UPPERCASE = [letter for letter in ALPHABET_UPPERCASE if not is_vowel(letter)]
CONSONANTS = CONSONANTS_LOWERCASE + CONSONANTS_UPPERCASE

MATH_MODES = ['align', 'equation', 'multline']

# ==============================================================================
# RULES
# ==============================================================================
WORDS = []

# Rule #1 - article 'a' followed by a word starting with a vowel
WORDS += [' a ' + vowel for vowel in VOWELS]
WORDS += ['A ' + vowel for vowel in VOWELS]

# Rule #2 - article 'an' followed by a consonant
WORDS += [' an ' + vowel for vowel in CONSONANTS]
WORDS += ['An ' + vowel for vowel in CONSONANTS]

# Repeated words
WORDS += ['the the ', ' an an ', ' a a ', ' ,', ]


# Math mode
def make_begin(mode):
    return '\\begin{' + mode + '}'


def make_end(mode):
    return '\\end{' + mode + '}'


# ==============================================================================
# FUNCTIONS
# ==============================================================================

def list_files_in_path(folder, endswith=None, filtering=None):
    """
        Look for files in folder (and sub-folders of that folder)
        for files that ends with 'endswith'
    """

    files_list = []
    for root, dirs, file_list in os.walk(folder):
        for file in file_list:
            if endswith is not None:
                if file.endswith(endswith):
                    files_list.append(os.path.join(root, file))
            if filtering is not None:
                if filtering(file):
                    files_list.append(os.path.join(root, file))
            if filtering is None and endswith is None:
                files_list.append(os.path.join(root, file))
    return files_list


def check(file, words):
    """
        look for words in each line of file
    """
    global IGNORE_MATH_MODE
    errors_found_in_file = False
    if not isinstance(words, list):
        words = [words]
    f = open(file, 'r')
    k = 1
    math_mode_on = False
    for line in f:
        for word in words:
            # Check if starting math mode
            if IGNORE_MATH_MODE and any([(mode_begin in line) for mode_begin in map(make_begin, MATH_MODES)]):
                math_mode_on = True

            # Check for rules per se
            if word in line and not math_mode_on:
                print('File: {}, line: {} -- Found: "{}" | {}'.format(os.path.basename(fil), k, word,
                                                                      line.replace(word, '[' + word + ']')))
                errors_found_in_file = True
            # Check if ending math mode
            if any([(mode_end in line) for mode_end in map(make_end, MATH_MODES)]) and IGNORE_MATH_MODE:
                math_mode_on = False
        k = k + 1
    return errors_found_in_file


# Create parser for the file
parser = argparse.ArgumentParser(description='Checks errors in TEX files that are not catch by spell checkers.\n \n'
                                             'Example: "an car", "the the house", "a orange", etc. \n \n'
                                             'Errors found are marked with brackets [], '
                                             'for instance: a[n c]ar, [a o]range.')
parser.add_argument('--process_math_env',
                    action='store_false', default=True, dest='IGNORE_MATH_MODE',
                    help='By default it does not process what is inside math environments '
                         'that starts with \\begin{...}.')
parser.add_argument('-p', '--path', type=str, action='store', default=os.path.dirname(os.path.abspath(__file__)),
                    help='By default the script runs in the current folder, use -p "PATH" to indicate the path or file '
                         'to be checked.')

if __name__ == '__main__':
    files = []
    ERRORS_FOUND = False
    # if a path is passed as an argument of the script use it, otherwise use the default
    args = parser.parse_args()
    PATH = args.path
    IGNORE_MATH_MODE = args.IGNORE_MATH_MODE

    if PATH.lower().endswith('.tex'):
        files = [PATH]
    else:
        # Replace the '\' (windows' default folder separator, to '/' which is python's default)
        PATH = PATH.replace('\\', '/')
        # Look for .tex files in PATH subfolders
        files = list_files_in_path(PATH, '.tex')
    # For each file look for the WORDS
    for fil in files:
        ERRORS_FOUND = ERRORS_FOUND or check(fil, WORDS)

    # If no error is found report to the user
    if not ERRORS_FOUND:
        print("No error found! \n Files checked:")
        for fil in files:
            print(fil)
