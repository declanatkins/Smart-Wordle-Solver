'''
Solves using information based random guesses, basically the most
naive way to play the game, while still using the information gained
by correct and partially correct words.
'''
import random
from . import util


def select_word(letter_status, corpus):
    filtered_corpus = [word for word in corpus if util.matches_letter_status(word, letter_status)]
    return filtered_corpus[random.randint(0, len(filtered_corpus) - 1)]


def solve(target_word):
    letter_status = util.build_letter_status()
    corpus = util.load_words()

    solved = False
    guesses = []
    while not solved:
        guess_word = select_word(letter_status, corpus)
        guesses.append(guess_word)
        correct, partially_correct = util.check_word(guess_word, target_word)
        if all(correct):
            solved = True
        else:
            letter_status = util.update_letter_status(guess_word, correct, partially_correct, letter_status)
    return guesses



