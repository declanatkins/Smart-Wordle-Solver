import string
import re
from functools import lru_cache, wraps


@lru_cache(maxsize=64)
def load_words():
    with open('data/allowed_words') as words_f:
        return [word.strip() for word in words_f]


def matches_letter_status(word, letter_status):
    pattern = ''
    for letter_pattern in letter_status['regexes']:
        pattern += f'[{"".join(letter_pattern)}]'

    if not re.search(pattern, word):
        return False
    
    for letter in letter_status['must_include']:
        if not word.count(letter) >= letter_status['must_include'].count(letter):
            return False

    return True


def build_letter_status():
    return {
        'regexes': 5 * [[l for l in string.ascii_lowercase]],
        'must_include': []
    }


def update_letter_status(word, correct, partially_correct, letter_status):
    
    new_must_include = []
    for i, (letter, c_val, pc_val) in enumerate(zip(word, correct, partially_correct)):
        if c_val:
            letter_status['regexes'][i] = letter
        elif pc_val:
            letter_status['regexes'][i] = [l for l in letter_status['regexes'][i] if l != letter]
            new_must_include.append(letter)
        else:
            letter_status['regexes'][i] = [l for l in letter_status['regexes'][i] if l != letter]
            if word.count(letter) == 1:
                for j, _ in enumerate(word):
                    letter_status['regexes'][j] = [l for l in letter_status['regexes'][j] if l != letter]
    
    old_must_include = letter_status['must_include']
    letter_status['must_include'] = []
    for letter in string.ascii_lowercase:
        letter_status['must_include'] += max(new_must_include.count(letter), old_must_include.count(letter)) * [letter]
    return letter_status


def check_word(guess_word, target_word):
    correct_letters = [guess_l == target_l for guess_l, target_l in zip(guess_word, target_word)]
    
    partially_correct_letters = []
    for i, guess_l in enumerate(guess_word):
        if correct_letters[i]:
            partially_correct_letters.append(False)
        else:
            target_letter_count = target_word.count(guess_l)
            guess_letter_count = guess_word.count(guess_l)
            if not target_letter_count:
                partially_correct_letters.append(False)
            elif target_letter_count >= guess_letter_count:
                partially_correct_letters.append(True)
            elif target_letter_count < guess_letter_count:
                # if this is the first index of the letter that is not correct
                # and the number of correct values is less than the count in the
                # word

                letter_indices = []
                word_list = [letter for letter in guess_word]
                while guess_l in word_list:
                    letter_indices.append(word_list.index(guess_l))
                    word_list = word_list[letter_indices[-1] + 1:] 
                
                n_correct = 0
                correct_idxs = []
                for idx in letter_indices:
                    if correct_letters[idx]:
                        n_correct += 1
                        correct_idxs.append(idx)
                
                if n_correct == target_letter_count:
                    partially_correct_letters.append(False)
                else:
                    partially_correct_count = target_letter_count - n_correct
                    other_idxs = [idx for idx in letter_indices if idx not in correct_idxs]

                    if i in other_idxs[:partially_correct_count]:
                        partially_correct_letters.append(True)
                    else:
                        partially_correct_letters.append(False)

    return correct_letters, partially_correct_letters
