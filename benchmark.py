"""
Empirical Performance and Attack Benchmarking Suite
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
Complex Computing Problem [CLO3]

Benchmarks:
1. Encryption / Decryption Execution Time & Throughput across input lengths.
2. Comparative Analysis: Custom Two-Stage Hybrid (Vigenere + Hill) vs Single-Stage Shift Cipher.
3. Attack Computational Effort & Success Rate across ciphertext lengths.
4. Letter frequency / Index of Coincidence of each cipher against English.

Running this file writes results.json, the only source of the numbers in the
plots and the PDF report.
"""

import json
import os
import platform
import random
import statistics
import string
import time
from typing import Dict, List
from pydoc_data.topics import topics
from custom_cipher import CustomHybridCipher, ShiftCipher, clean_text
from attack import KnownPlaintextAttacker, FrequencyAnalyzer, ENGLISH_FREQ, _precompute_gl2

SEED = 486  # fixed so every run tests the same keys and messages
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


def english_corpus() -> str:
    """Real English prose: Python's bundled documentation (about 378,000 letters, no download)."""
    return clean_text(" ".join(topics.values()))


def random_message(rng: random.Random, corpus: str, length: int) -> str:
    start = rng.randrange(len(corpus) - length)
    return corpus[start:start + length]


def random_cipher(rng: random.Random) -> CustomHybridCipher:
    """A fresh cipher with a random Vigenere key of 10-20 letters and random Hill phrase."""
    vigenere_key = "".join(rng.choices(string.ascii_uppercase, k=rng.randint(10, 20)))
    hill_key = "".join(rng.choices(string.ascii_uppercase, k=12))
    return CustomHybridCipher(vigenere_key, hill_key)


def generate_synthetic_english_text(length: int) -> str:
    """Generates synthetic English-like text based on repeated standard passages."""
    base = (
        "THEIMPACTOFCRYPTOGRAPHYONMODERNNETWORKSECURITYCANNOTBEOVERSTATED"
        "CONFIDENTIALITYAUTHENTICATIONINTEGRITYANDNONREPUDIATIONFORMTHE"
        "COREPILLARSOFINFORMATIONASSURANCEINCOMPLEXCOMPUTINGSYSTEMS"
    )
    repeat_count = (length // len(base)) + 1
    return (base * repeat_count)[:length]


def benchmark_ciphers() -> List[Dict]:
    """
    Benchmarks encryption & decryption latency for:
    - Custom Hybrid Cipher (Vigenere + Hill)
    - Shift (Caesar) Cipher
    across sizes: 100, 500, 1000, 5000, 10000 characters.
    """
    vigenere_key = "CRYPTOGRAPHYKEY"   # len 15
    hill_key = "HILLCIPHERKEY"         # len 13
    custom_cipher = CustomHybridCipher(vigenere_key, hill_key)
    shift_cipher = ShiftCipher(shift=5)

    lengths = [100, 500, 1000, 5000, 10000]
    iterations = 50
    results = []

    print("\n" + "=" * 90)
    print("      CIPHER PERFORMANCE BENCHMARK (VIGENERE + HILL HYBRID VS SHIFT CIPHER)")
    print("=" * 90)
    header = f"{'Length (chars)':<15} | {'Custom Enc (ms)':<16} | {'Custom Dec (ms)':<16} | {'Shift Enc (ms)':<15} | {'Shift Dec (ms)':<15}"
    print(header)
    print("-" * 90)

    for length in lengths:
        plaintext = generate_synthetic_english_text(length)

        # Custom Cipher Encryption
        t0 = time.perf_counter()
        for _ in range(iterations):
            c_custom = custom_cipher.encrypt(plaintext)
        t_custom_enc = ((time.perf_counter() - t0) / iterations) * 1000.0

        # Custom Cipher Decryption
        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = custom_cipher.decrypt(c_custom)
        t_custom_dec = ((time.perf_counter() - t0) / iterations) * 1000.0

        # Shift Cipher Encryption
        t0 = time.perf_counter()
        for _ in range(iterations):
            c_shift = shift_cipher.encrypt(plaintext)
        t_shift_enc = ((time.perf_counter() - t0) / iterations) * 1000.0

        # Shift Cipher Decryption
        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = shift_cipher.decrypt(c_shift)
        t_shift_dec = ((time.perf_counter() - t0) / iterations) * 1000.0

        row = {
            "length": length,
            "custom_enc_ms": round(t_custom_enc, 4),
            "custom_dec_ms": round(t_custom_dec, 4),
            "shift_enc_ms": round(t_shift_enc, 4),
            "shift_dec_ms": round(t_shift_dec, 4),
        }
        results.append(row)
        print(f"{length:<15} | {t_custom_enc:<16.4f} | {t_custom_dec:<16.4f} | {t_shift_enc:<15.4f} | {t_shift_dec:<15.4f}")

    return results


def attack_trials(length: int, known: int, trials: int, rng: random.Random, corpus: str) -> Dict:
    """Runs the attack on random keys and messages. Success means the exact full message came back."""
    successes = 0
    times_ms, matrices = [], []
    for _ in range(trials):
        cipher = random_cipher(rng)
        plaintext = random_message(rng, corpus, length)
        res = KnownPlaintextAttacker.attack(cipher.encrypt(plaintext), plaintext[:known])
        successes += res["recovered_full_plaintext"] == plaintext
        times_ms.append(res["elapsed_seconds"] * 1000.0)
        matrices.append(res["matrices_evaluated"])
    return {
        "length": length,
        "known_chars": known,
        "trials": trials,
        "success_rate": round(100.0 * successes / trials, 1),
        "avg_time_ms": round(statistics.mean(times_ms), 2),
        "max_time_ms": round(max(times_ms), 2),
        "avg_matrices": round(statistics.mean(matrices)),
    }


def benchmark_attack(trials: int = 20) -> Dict:
    """
    Benchmarks the Known-Plaintext Attack with the key length unknown to the attacker:
    - by_length: 25% of each message is known, across ciphertext lengths.
    - by_known: fixed 1,000-letter messages, varying how much is known.
    """
    rng = random.Random(SEED)
    corpus = english_corpus()
    header = f"{'Length (chars)':<15} | {'Known Chars':<12} | {'Success Rate':<13} | {'Avg Time (ms)':<14} | {'Max Time (ms)':<14} | {'Avg Matrices':<12}"

    def run(title, cases):
        print("\n" + "=" * 96)
        print(f"  {title} ({trials} random key/message trials per row)")
        print("=" * 96)
        print(header)
        print("-" * 96)
        rows = []
        for length, known in cases:
            row = attack_trials(length, known, trials, rng, corpus)
            rows.append(row)
            print(f"{length:<15} | {known:<12} | {row['success_rate']:<13} | {row['avg_time_ms']:<14} | {row['max_time_ms']:<14} | {row['avg_matrices']:<12}")
        return rows

    return {
        "by_length": run("KPA SUCCESS BY CIPHERTEXT LENGTH (25% OF MESSAGE KNOWN)",
                         [(n, n // 4) for n in [50, 100, 150, 200, 500, 1000, 5000, 10000]]),
        "by_known": run("KPA SUCCESS BY AMOUNT OF KNOWN PLAINTEXT (1,000-LETTER MESSAGES)",
                        [(1000, m) for m in [20, 30, 34, 36, 40, 50, 60, 100]]),
    }


def benchmark_frequency(samples: int = 30, length: int = 5000) -> Dict:
    """Compares each cipher's letter statistics against English, averaged over random keys."""
    rng = random.Random(SEED)
    corpus = english_corpus()
    series = {"Plaintext": [], "Shift": [], "Vigenere only": [], "Hill only": [], "Custom": []}
    changed_letters = []

    for _ in range(samples):
        plaintext = random_message(rng, corpus, length)
        cipher = random_cipher(rng)
        numbers = [ord(c) - 65 for c in plaintext]
        as_text = lambda nums: "".join(chr(n + 65) for n in nums)
        ciphertext = cipher.encrypt(plaintext)
        series["Plaintext"].append(plaintext)
        series["Shift"].append(ShiftCipher(rng.randrange(1, 26)).encrypt(plaintext))
        series["Vigenere only"].append(as_text(cipher._vigenere_encrypt(plaintext)))
        series["Hill only"].append(as_text(cipher._hill_encrypt(numbers)))
        series["Custom"].append(ciphertext)

        # Diffusion: how many ciphertext letters move when one plaintext letter changes
        position = rng.randrange(length)
        replacement = chr((ord(plaintext[position]) - 65 + rng.randrange(1, 26)) % 26 + 65)
        altered = cipher.encrypt(plaintext[:position] + replacement + plaintext[position + 1:])
        changed_letters.append(sum(x != y for x, y in zip(ciphertext, altered)))

    def summarise(texts):
        ranked = [sorted(FrequencyAnalyzer.calculate_frequencies(t).values(), reverse=True) for t in texts]
        return {
            "ioc": round(statistics.mean(FrequencyAnalyzer.calculate_ioc(t) for t in texts), 5),
            "ioc_stdev": round(statistics.stdev(FrequencyAnalyzer.calculate_ioc(t) for t in texts), 5),
            "chi_squared": round(statistics.mean(FrequencyAnalyzer.calculate_chi_squared(t) for t in texts), 1),
            "ranked_freq": [round(statistics.mean(column), 3) for column in zip(*ranked)],
        }

    result = {
        "samples": samples,
        "length": length,
        "english_ranked_freq": sorted(ENGLISH_FREQ.values(), reverse=True),
        "ciphers": {name: summarise(texts) for name, texts in series.items()},
        "avg_ciphertext_letters_changed": round(statistics.mean(changed_letters), 2),
        "max_ciphertext_letters_changed": max(changed_letters),
    }

    print("\n" + "=" * 90)
    print(f"  LETTER STATISTICS VS ENGLISH ({samples} random keys, {length}-letter messages)")
    print("=" * 90)
    for name, row in result["ciphers"].items():
        print(f"{name:<15} | IoC {row['ioc']:.5f} (sd {row['ioc_stdev']:.5f}) | Chi-squared vs English {row['chi_squared']}")
    print(f"One plaintext letter changed -> avg {result['avg_ciphertext_letters_changed']} ciphertext letters changed")
    return result


if __name__ == "__main__":
    started = time.perf_counter()
    _precompute_gl2()
    precompute_ms = (time.perf_counter() - started) * 1000.0
    results = {
        "environment": {"python": platform.python_version(), "machine": platform.processor() or platform.machine()},
        "gl2_precompute_ms": round(precompute_ms, 1),
        "ciphers": benchmark_ciphers(),
        "attack": benchmark_attack(),
        "frequency": benchmark_frequency(),
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print(f"\nSaved measurements to {RESULTS_PATH}")
