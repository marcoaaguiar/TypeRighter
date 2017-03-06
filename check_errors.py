import mmap
import os
import sys
import string
PATH = "C:\\Users\\marco\\Dropbox\\doutorado\\courses\\numerical_opt_control\\project\\num_opt_control_report\\"

#==============================================================================
# OPTIONS
#==============================================================================

IGNORE_EQUATIONS = True


#==============================================================================
# ALPHABET AND OTHER DEFINITIONS
#==============================================================================

ALPHABET_LOWERCASE = list(string.ascii_lowercase)
ALPHABET_UPPERCASE = list(string.ascii_uppercase )
ALPHABET = ALPHABET_LOWERCASE + ALPHABET_UPPERCASE

VOWELS_LOWERCASE = ['a','e','i','o','u']
VOWELS_UPPERCASE = ['A','E','I','O','U']
VOWELS = VOWELS_LOWERCASE + VOWELS_UPPERCASE

isVowel = lambda letter: letter in VOWELS

CONSONANTS_LOWERCASE = [ letter for letter in ALPHABET_LOWERCASE if not isVowel(letter)]
CONSONANTS_UPPERCASE = [ letter for letter in ALPHABET_UPPERCASE if not isVowel(letter)]
CONSONANTS = CONSONANTS_LOWERCASE + CONSONANTS_UPPERCASE

MATH_MODES = ['align', 'equation', 'multline']


#==============================================================================
# RULES
#==============================================================================
WORDS = []

# Rule #1 - article 'a' followed by a word starting with a vowel
WORDS += [' a '+ vowel for vowel in VOWELS]
WORDS += ['A '+ vowel for vowel in VOWELS]

# Rule #2 - article 'an' followe by a consonant
WORDS += [' an '+ vowel for vowel in CONSONANTS]
WORDS += ['An '+ vowel for vowel in CONSONANTS]

WORDS += ['the the ', ' an an ', ' a a ', ' ,', ]
		 
MATH_MODES_BEGIN = ['\\begin{'+ mode+'}' for mode in MATH_MODES]		 
MATH_MODES_END = ['\\end{'+ mode+'}' for mode in MATH_MODES]		 
ERRORS_FOUND = False

#==============================================================================
# FUNCTIONS
#==============================================================================
	 
def scanFiles(folder, key='.tex'):
    ''' 
        Look for files in folder (and subfolders of folder) 
        that has a 'key' in the name 
    '''
    files_list = []
    for root, dirs, files in os.walk(folder):
        for fil in files:
            if fil.endswith(key):
                 files_list.append(os.path.join(root, fil))
    return files_list

def check(fil, words):
    ''' 
        look for words in each line of fil
    '''
    global ERRORS_FOUND
    if not isinstance(words,list):
        words = [words]
    f = open(fil, 'r')
    k = 1
    MATH_MODE_ON = False
    for line in f:
        for word in words:
            # Check if starting math mode
            if IGNORE_EQUATIONS and any([(mode_begin in line) for mode_begin in MATH_MODES_BEGIN]):
                MATH_MODE_ON = True
            
            # Check for rules per se
            if word in line and not MATH_MODE_ON:
                print 'File: ', os.path.basename(fil), 'line: ',k,' Found: ',word, ' | ', line.replace(word, '['+word+']')
                ERRORS_FOUND = True
            # Check if ending math mode
            if any([(mode_end in line) for mode_end in MATH_MODES_END]) and IGNORE_EQUATIONS:
                MATH_MODE_ON = False
        k =k+1 
      
def scanAndCheck(path = PATH, key = '.tex', words = WORDS):
    files = scanFiles(PATH,key)
    for fil in files:
        check(fil, words)

if __name__ == '__main__':
    # if a path is passed as an argument of the script use it, otherwise use the default
	if not len(sys.argv) >0:
		PATH = sys.argv[1]
     #Replace the '\' (windows' default folder separator, to '/' which is python's default)
	PATH = PATH.replace('\\','/')
	
     # Look for .tex files in PATH subfolders
	files = scanFiles(PATH,'.tex')
     
     # For each file look for the WORDS
	for fil in files:
		check(fil, WORDS)
     # If no error is found report to the user
	if not ERRORS_FOUND:	
		print "No error found! \n Files checked:"
		for fil in files:
			print fil