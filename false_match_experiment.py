"""
How many known letters beyond one key period does the attack need?

Fixes the Vigenere key length at 20 and counts wrong answers for each amount of
redundancy R. Wrong answers are mostly the correct matrix mod 13 with an error
only mod 2, which is why attack.MIN_REDUNDANCY is 20. Takes about 2 minutes.
"""
import random
import string

import attack as A
from benchmark import SEED, english_corpus, random_message
from custom_cipher import CustomHybridCipher

rng = random.Random(SEED)
corpus = english_corpus()
TRIALS = 150

for R in (4, 8, 12, 16, 20):
    A.MIN_REDUNDANCY = R
    wrong = wrong_mod2_only = 0
    for _ in range(TRIALS):
        vigenere_key = "".join(rng.choices(string.ascii_uppercase, k=20))
        cipher = CustomHybridCipher(vigenere_key, "".join(rng.choices(string.ascii_uppercase, k=12)))
        plaintext = random_message(rng, corpus, 400)
        result = A.KnownPlaintextAttacker.attack(cipher.encrypt(plaintext), plaintext[:20 + R], vigenere_key_len=20)
        if result["recovered_full_plaintext"] != plaintext:
            wrong += 1
            found = result["recovered_hill_mat"]
            if found and all((x - y) % 13 == 0 for x, y in zip(found, cipher.hill_mat)):
                wrong_mod2_only += 1
    print(f"R={R:<3} wrong={wrong}/{TRIALS} ({100 * wrong / TRIALS:.1f}%), of which correct mod 13: {wrong_mod2_only}")
