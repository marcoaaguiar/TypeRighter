import argparse
import os
import string

# ==============================================================================
# OPTIONS
# ==============================================================================
import textwrap

IGNORE_ENVIRONMENT = True
IGNORED_LATEX_ENVIRONMENTS = ['align', 'equation', 'multline',
                              'tabular', 'program', 'algorithm', 'algorithmic', 'algorithm2e']
IGNORED_LATEX_ENVIRONMENTS = IGNORED_LATEX_ENVIRONMENTS + [e + '*' for e in IGNORED_LATEX_ENVIRONMENTS]

# ==============================================================================
# INITIALIZE VARIABLES
# ==============================================================================

PATH = ""
RULES_LIST = []


# ==============================================================================
# RULES
# ==============================================================================

def rule_search_for_match(file, search_terms, error_explanation_generator=None):
    if error_explanation_generator is None:
        def error_explanation_generator(case):
            return 'Found match for: {}'.format(case)
    errors = []

    for line_number, line in enumerate(file):
        #  In case of hard wrapping (line break if number of char greater than some number)
        #  Create an augmented line (current line + next).

        for term in search_terms:
            if term in line:
                errors.append({
                    'line_number': line_number + 1,
                    'error_explanation': error_explanation_generator(term),
                    'line': line.replace(term, '[' + term + ']')
                })
    return errors


def rule_article_a(file):
    # All vowels
    vowels_lowercase = 'aeiou'
    vowels_uppercase = 'AEIOU'
    vowels = tuple(vowels_lowercase + vowels_uppercase)

    # Article a followed by a Vowel
    articles = ['A', 'a']

    errors = []
    last_word = ''

    for line_number, line in enumerate(file):
        words_in_line = line.split()
        for word_index, word in enumerate(words_in_line):
            if word.startswith(vowels):
                for art in articles:
                    if last_word == art:
                        if word_index == 0:  # if this line continues the previous line (hard wrap)
                            error_line_number = (line_number + 1) - 1
                            error_line_display = file[line_number - 1].replace(last_word, '[' + last_word) \
                                                 + ' <line break> ' + line.replace(word, word + ']')
                        else:
                            error_line_number = (line_number + 1)
                            error_line_display = line.replace(last_word + ' ' + word,
                                                              '[' + last_word + ' ' + word + ']')

                        errors.append({
                            'line_number': error_line_number,
                            'error_explanation': 'Article "a" followed by a vowel: {}'.format(art + ' ' + word),
                            'line': error_line_display
                        })
            last_word = word

    return errors


def rule_article_an(file):
    # Vowels and consonants
    vowels_lowercase = tuple('aeiou')
    vowels_uppercase = tuple('AEIOU')
    vowels = tuple(vowels_lowercase + vowels_uppercase)

    consonants_lowercase = [l for l in string.ascii_lowercase if l not in vowels]
    consonants_uppercase = [l for l in string.ascii_uppercase if l not in vowels]
    consonants = tuple(consonants_lowercase + consonants_uppercase)

    articles = ['An', 'an']
    # Search Terms:
    errors = []
    last_word = ''

    for line_number, line in enumerate(file):
        words_in_line = line.split()
        for word_index, word in enumerate(words_in_line):
            if word.startswith(consonants):
                for art in articles:
                    if last_word == art:
                        if word_index == 0:  # if this line continues the previous line (hard wrap)
                            error_line_number = (line_number + 1) - 1
                            error_line_display = file[line_number - 1].replace(last_word, '[' + last_word) \
                                                 + ' <line break> ' + line.replace(word, word + ']')
                        else:
                            error_line_number = (line_number + 1)
                            error_line_display = line.replace(last_word + ' ' + word,
                                                              '[' + last_word + ' ' + word + ']')

                        errors.append({
                            'line_number': error_line_number,
                            'error_explanation': 'Article "an" followed by a consonant: {}'.format(art + ' ' + word),
                            'line': error_line_display
                        })
            last_word = word

    return errors


def rule_punctuation(file):
    search_terms = [' .', ' :', '...', ' ,', ' ;', ' ?', ' !']

    def error_explanation_generator(case):
        if case == '...':
            return 'Punctuation error: "{}" use "\\dots" instead'.format(case)
        return 'Punctuation error: "{}"'.format(case)

    errors = rule_search_for_match(file, search_terms, error_explanation_generator)

    return errors


def rule_duplicate_word(file):
    words_allowed_to_be_duplicate = ['&']

    errors = []
    last_word = ''

    for line_number, line in enumerate(file):
        words_in_line = line.split()
        for word_index, word in enumerate(words_in_line):
            if not word.startswith('\\') \
                    and word not in words_allowed_to_be_duplicate \
                    and '%' not in word:  # commands can be duplicate too, comments can be ignored
                if word.lower() == last_word.lower():
                    if word_index == 0:  # if this line continues the previous line (hard wrap)
                        error_line_number = (line_number + 1) - 1
                        error_line_display = file[line_number - 1].replace(last_word,
                                                                           '[' + last_word) + ' <line break> ' + line.replace(
                            word, word + ']')
                    else:
                        error_line_number = (line_number + 1)
                        error_line_display = line.replace(last_word + ' ' + word, '[' + last_word + ' ' + word + ']')
                    errors.append({
                        'line_number': error_line_number,
                        'error_explanation': 'Repeated words: {} == {}'.format(last_word, word),
                        'line': error_line_display
                    })
            last_word = word

    return errors


RULES_LIST.append(rule_article_a)
RULES_LIST.append(rule_article_an)
RULES_LIST.append(rule_punctuation)
RULES_LIST.append(rule_duplicate_word)


# ==============================================================================
# UTILITY
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


def remove_ignored_latex_environments(file):
    inside_env = False
    output = []
    global IGNORE_ENVIRONMENT
    global IGNORED_LATEX_ENVIRONMENTS

    begin_envs_list = ['\\begin{' + env + '}' for env in IGNORED_LATEX_ENVIRONMENTS]
    end_envs_list = ['\\end{' + env + '}' for env in IGNORED_LATEX_ENVIRONMENTS]

    for line in file:
        # Check if starting math mode
        if IGNORE_ENVIRONMENT and any([(begin_env in line) for begin_env in begin_envs_list]):
            inside_env = True

        # Check for rules per se
        if not inside_env:
            output.append(line)
        else:
            output.append('%')

        # Check if ending math mode
        if any([(end_env in line) for end_env in end_envs_list]) and IGNORE_ENVIRONMENT:
            inside_env = False

    return output


def remove_comment_lines(file):
    output = []

    for line in file:
        # split the line in words
        words_in_line = line.split()

        # list of words to be written in the output version of the current line
        output_line_list = []
        for word in words_in_line:
            # if a "%" is identified stop reading the line
            if word.startswith('%'):
                output_line_list.append('%')
                break
            else:
                # else add the word to the output
                output_line_list.append(word)

        output.append(' '.join(output_line_list))

    return output


def check(filename):
    """
        look for words in each line of filename
    """
    global IGNORE_ENVIRONMENT
    global RULES_LIST

    file_errors = []

    #  Open file and remove undesired lines
    file = open(filename, 'r')
    lines = remove_ignored_latex_environments(file)
    lines = remove_comment_lines(lines)

    #  Apply the rules
    for rule in RULES_LIST:
        file_errors += rule(lines)

    # Sort the errors by line number
    file_errors.sort(key=lambda x: x['line_number'])
    found_error = len(file_errors) > 0

    #  If file has any error, print them
    if found_error:
        print_file_errors(filename, file_errors)

    return found_error


def print_file_errors(filename, errors):
    base_filename = os.path.basename(filename)
    header = (' ' + base_filename + ' ').center(40, '=')
    print(header)

    for error in errors:
        print('{:20} {}'.format('Line number: ', error['line_number']))
        print('{:20} {}'.format('Error message: ', error['error_explanation']))

        wrapped_lines = textwrap.wrap(error['line'])

        print('{:20} {}'.format('Line: ', wrapped_lines[0]))
        for sentence in wrapped_lines[1:]:
            print('{:20} {}'.format('', sentence))

        print('')


# ==============================================================================
# PARSER
# ==============================================================================

# Create parser for the file
parser = argparse.ArgumentParser(description='Checks errors in TEX files that are not catch by spell checkers.\n \n'
                                             'Example: "an car", "the the house", "a orange", etc. \n \n'
                                             'Errors found are marked with brackets [], '
                                             'for instance: a[n c]ar, [a o]range.')
parser.add_argument('-p', '--path', type=str, action='store', default=os.path.dirname(os.path.abspath(__file__)),
                    help='By default the script runs in the current folder, use -p "PATH" to indicate the path or file '
                         'to be checked.')
parser.add_argument('--process_ignored_environments',
                    action='store_false', default=True, dest='IGNORE_ENVIRONMENT',
                    help='By default it does not process what is inside of some environments'
                         'that starts with \\begin{{...\}}. '
                         'Ignored envs: {}'.format(IGNORED_LATEX_ENVIRONMENTS))
parser.add_argument('-e', '--extension', action='store', default='.tex',
                    help='Files extension to be searched on the folders')

parser.add_argument('-w', '--words', action='store', default=[],
                    nargs='*', help='Search for words and expressions in the document. Example: -w Lagrange "a NLP"')

# ==============================================================================
# __MAIN__
# ==============================================================================

if __name__ == '__main__':
    files = []
    ERRORS_FOUND = False
    # if a path is passed as an argument of the script use it, otherwise use the default
    args = parser.parse_args()
    PATH = args.path
    IGNORE_ENVIRONMENT = args.IGNORE_ENVIRONMENT
    EXTENSION = args.extension
    EXTRA_SEARCH_TERMS = args.words

    RULES_LIST.append(lambda file: rule_search_for_match(file, EXTRA_SEARCH_TERMS))

    if PATH.lower().endswith('.tex'):
        files = [PATH]
    else:
        # Replace the '\' (windows' default folder separator, to '/' which is python's default)
        PATH = PATH.replace('\\', '/')
        # Look for .tex files in PATH sub-folders
        files = list_files_in_path(PATH, EXTENSION)

    # If given PATH has no .tex files report it!
    if len(files) == 0:
        print('No files found in PATH: {}'.format(PATH))
    else:
        # For each file look for the WORDS
        for f in files:
            file_has_error = check(f)
            ERRORS_FOUND = ERRORS_FOUND or file_has_error

        # If no error is found report to the user
        if not ERRORS_FOUND:
            print("No error found! \n Files checked:")
            for fil in files:
                print(fil)
