"""
Empirical Performance and Attack Benchmarking Suite
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
Complex Computing Problem [CLO3]

Benchmarks:
1. Encryption / Decryption Execution Time & Throughput across input lengths.
2. Comparative Analysis: Custom Two-Stage Hybrid (Vigenere + Hill) vs Single-Stage Shift Cipher.
3. Attack Computational Effort & Success Rate across ciphertext lengths.
"""

import time
import random
import string
from typing import Dict, List
from custom_cipher import CustomHybridCipher, ShiftCipher, clean_text
from attack import KnownPlaintextAttacker, FrequencyAnalyzer


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


def benchmark_attack() -> List[Dict]:
    """
    Benchmarks Known-Plaintext Attack computational effort and success rate across lengths.
    """
    vigenere_key = "CYBERDEFENSEKEY"    # len 15
    hill_key = "HILLCIPHERKEY"          # len 13
    cipher = CustomHybridCipher(vigenere_key, hill_key)

    lengths = [100, 250, 500, 1000]
    known_prefix_len = 36
    trials = 5
    attack_results = []

    print("\n" + "=" * 90)
    print("        KNOWN-PLAINTEXT ATTACK (KPA) COMPUTATIONAL EFFORT ON HYBRID CIPHER")
    print("=" * 90)
    header = f"{'Length (chars)':<15} | {'Known Chars':<15} | {'Success Rate':<15} | {'Avg Time (ms)':<18} | {'Avg Matrices':<15}"
    print(header)
    print("-" * 90)

    for length in lengths:
        success_count = 0
        total_time = 0.0
        total_matrices = 0

        for trial in range(trials):
            plaintext = generate_synthetic_english_text(length)
            ciphertext = cipher.encrypt(plaintext)
            known_prefix = plaintext[:known_prefix_len]

            res = KnownPlaintextAttacker.attack(
                ciphertext=ciphertext,
                known_prefix=known_prefix,
                vigenere_key_len=len(vigenere_key)
            )

            expected_pt = plaintext if len(plaintext) % 2 == 0 else plaintext + 'X'
            if res["success"] and res["recovered_full_plaintext"] == expected_pt:
                success_count += 1
            total_time += res["elapsed_seconds"]
            total_matrices += res["matrices_evaluated"]

        avg_time_ms = (total_time / trials) * 1000.0
        avg_matrices = total_matrices / trials
        success_rate = (success_count / trials) * 100.0

        row = {
            "length": length,
            "known_chars": known_prefix_len,
            "success_rate": f"{success_rate:.1f}%",
            "avg_time_ms": round(avg_time_ms, 3),
            "avg_matrices": round(avg_matrices, 1)
        }
        attack_results.append(row)
        print(f"{length:<15} | {known_prefix_len:<15} | {row['success_rate']:<15} | {avg_time_ms:<18.3f} | {avg_matrices:<15.1f}")

    return attack_results


if __name__ == "__main__":
    benchmark_ciphers()
    benchmark_attack()
