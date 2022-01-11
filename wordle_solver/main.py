import os
import argparse
import hashlib
import importlib
import random
import time
from tqdm import tqdm
from colorama import Back, Fore, Style


def _load_words(corpus=''):
    if corpus:
        with open(corpus) as words_f:
            return [word.strip() for word in words_f]
    else:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/allowed_words')) as words_f:
            return [word.strip() for word in words_f]


def _pick_target_word():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/correct_hashes')) as words_f:
        target_hashes = [word.strip() for word in words_f]
    allowed_words = _load_words()
    index = random.randint(0, len(target_hashes) - 1)
    target_hash = target_hashes[index]

    for word in allowed_words:
        if str(hashlib.md5(word.encode()).hexdigest()) == target_hash:
            return word
    
    raise ValueError('Couldn\'t find the word')
    

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
                if target_letter_count >= guess_word[:i+1].count(guess_l):
                    partially_correct_letters.append(True)
                else:
                    partially_correct_letters.append(False)

    return correct_letters, partially_correct_letters


def evaluate(args):
    solver = importlib.import_module(f'solvers.{args.solver_name}')
    allowed_words = _load_words(args.corpus)

    guess_counts = []
    times = []
    for word in tqdm(allowed_words):
        start_time = time.time()
        guesses = solver.solve(word)
        end_time = time.time()
        times.append(end_time - start_time)
        
        for guess in guesses:
            if guess not in allowed_words:
                raise ValueError(f'Only valid words can be guessed! - {guess} is invalid')
        guess_counts.append(len(guesses))
    
    print(f'Average guesses needed: {sum(guess_counts/len(guess_counts))}')
    print(f'Average time needed: {sum(times)/len(times)}')


def play(input_word='', max_guesses=6):
    guesses_left = max_guesses
    words = _load_words()
    target_word = input_word or _pick_target_word()

    guessed_words = []

    while guesses_left:

        valid = False
        while not valid:
            guess = input('Please enter a word:')
            if guess in guessed_words:
                print(f'You\'ve already guessed {guess}!')
            elif len(guess) != 5:
                print('Your guess should have 5 letters!')
            elif guess not in words:
                print(f'{guess} is not a valid word!')
            else:
                valid = True

        correct, partially_correct = check_word(guess, target_word)
        result_str = Fore.BLACK
        for letter, correct_val, partially_correct_val in zip(guess, correct, partially_correct):
            if correct_val:
                result_str += Back.GREEN
            elif partially_correct_val:
                result_str += Back.YELLOW
            else:
                result_str += Back.RED
            result_str += letter
        print(result_str + Style.RESET_ALL)
        guessed_words.append(guess)
        guesses_left -= 1

        if all(correct):
            print(f'Congratulations you got the answer in {len(guessed_words)} guesses!')
            break
    if not guesses_left:
        print('You\'re out of guesses, game over :(')
        print('The word was:', target_word)


def challenge(args):
    target_word = _pick_target_word()

    solver = importlib.import_module(f'solvers.{args.solver_name}')
    guesses = solver.solve(target_word)

    print(f'The solver took {len(guesses)} guesses, can you beat it?!')
    play(target_word, len(guesses))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda _: play())
    subparsers = parser.add_subparsers()

    play_parser = subparsers.add_parser('play')
    play_parser.add_argument('--guesses', type=int, default=6, help='The number of guesses allowed')
    play_parser.set_defaults(func=lambda args: play(max_guesses=args.guesses))

    eval_parser = subparsers.add_parser('eval')
    eval_parser.add_argument('solver_name', type=str, help='The solver module to evaluate')
    eval_parser.add_argument('--corpus', type=str, default='', help='An alternate word corpus to use')
    eval_parser.set_defaults(func=eval)

    challenge_parser = subparsers.add_parser('challenge')
    challenge_parser.add_argument('solver_name', type=str, help='The solver module to evaluate')
    challenge_parser.set_defaults(func=challenge)

    args = parser.parse_args()
    args.func(args)