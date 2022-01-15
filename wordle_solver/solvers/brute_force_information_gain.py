from collections import defaultdict
from . import util



def letter_analysis(filtered_corpus):
    letter_data = defaultdict(lambda: [0, 0, 0, 0, 0])

    total_word_count = len(filtered_corpus)
    for word in filtered_corpus:
        for i, letter in enumerate(word):
            letter_data[letter][i] += 1 / total_word_count

    return letter_data


def select_word(letter_status, corpus):
    filtered_corpus = [word for word in corpus if util.matches_letter_status(word, letter_status)]

    letter_analysis_results = letter_analysis(filtered_corpus)

    word_scores = []
    for word in filtered_corpus:
        score = 0
        for i, letter in enumerate(word):
            if word.index(letter) == i:
                letter_scores = letter_analysis_results[letter].copy()
                index_score = letter_scores[i]
                
                del letter_scores[i]
                other_index_score = 0.2 * sum(letter_scores)
                score += index_score + other_index_score
    
        word_scores.append((word, score))
    sorted_scores = sorted(word_scores, reverse=True, key=lambda x: x[1])
    return sorted_scores[0][0]


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
