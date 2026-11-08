"""
Main Interactive Console Application
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
CLO: Complex Computing Problem [CLO3]
Project: Design and Break a Custom Cipher Based on Classical Techniques

Techniques Selected from Course Syllabus:
- 3-Vigenere-Cipher.pdf (Stage 1: Polyalphabetic Substitution - Confusion)
- 7-Hill-Ciphers.pdf    (Stage 2: Polygraphic Block Linear Algebra - Diffusion)
- 2-Shift-Cipher.pdf    (Baseline Comparison)
"""

import sys
import time
from custom_cipher import CustomHybridCipher, clean_text
from attack import FrequencyAnalyzer, KnownPlaintextAttacker
from benchmark import benchmark_ciphers, benchmark_attack


def print_banner():
    print("""
========================================================================
  NETWORK AND INFORMATION SECURITY (CT-486) - COMPLEX COMPUTING PROBLEM
  DESIGN AND BREAK A CUSTOM CIPHER BASED ON CLASSICAL TECHNIQUES [CLO3]
========================================================================
  [+] Stage 1: Polyalphabetic Substitution (Vigenere Cipher) [Confusion]
  [+] Stage 2: Polygraphic Block Transformation (Hill Cipher) [Diffusion]
  [+] Baseline Comparison: Shift (Caesar) Cipher
  [+] Enforced Minimum Key Length: >= 10 characters
========================================================================
""")


def run_full_walkthrough():
    print("\n>>> EXECUTING AUTOMATED COMPREHENSIVE WALKTHROUGH <<<\n")

    vigenere_key = "CRYPTOGRAPHYKEY"   # 15 chars
    hill_key = "HILLCIPHERKEY"         # 13 chars
    print(f"[*] Initializing Custom Hybrid Cipher (Vigenere + Hill):")
    print(f"    - Stage 1 Vigenere Key : '{vigenere_key}' (Length: {len(vigenere_key)})")
    print(f"    - Stage 2 Hill Key     : '{hill_key}' (Length: {len(hill_key)})")

    cipher = CustomHybridCipher(vigenere_key, hill_key)
    print(f"    - Generated 2x2 Hill Key Matrix: {cipher.hill_mat[:2]}")
    print(f"                                     {cipher.hill_mat[2:]}")

    sample_message = (
        "CONFIDENTIALCOMMUNICATIONFORNETWORKANDINFORMATIONSECURITYLABORATORY"
        "ALLSTUDENTSMUSTIMPLEMENTANDCRYPTANALYZECLASSICALCIPHERTECHNIQUES"
    )

    print(f"\n[1] ENCRYPTION PHASE:")
    print(f"    Plaintext (N={len(sample_message)} chars):")
    print(f"    \"{sample_message}\"")

    ciphertext = cipher.encrypt(sample_message)
    print(f"\n    Ciphertext Generated:")
    print(f"    \"{ciphertext}\"")

    print(f"\n[2] DECRYPTION PHASE:")
    decrypted = cipher.decrypt(ciphertext)
    print(f"    Decrypted Plaintext:")
    print(f"    \"{decrypted}\"")
    match = (decrypted == sample_message)
    print(f"    Integrity Verification (Original == Decrypted): {match}")

    print(f"\n[3] STATISTICAL & FREQUENCY ANALYSIS:")
    stats = FrequencyAnalyzer.analyze(sample_message, ciphertext)
    print(f"    - Plaintext Index of Coincidence (IoC)  : {stats['plaintext_ioc']:.5f} (English Ref: ~0.0667)")
    print(f"    - Ciphertext Index of Coincidence (IoC) : {stats['ciphertext_ioc']:.5f} (Polyalphabetic/Random Ref: ~0.0385)")
    print(f"    - Plaintext Chi-Squared Statistic      : {stats['plaintext_chi_sq']:.2f}")
    print(f"    - Ciphertext Chi-Squared Statistic     : {stats['ciphertext_chi_sq']:.2f}")
    print(f"    - Top 5 Plaintext Letters              : {stats['top_plaintext_letters']}")
    print(f"    - Top 5 Ciphertext Letters             : {stats['top_ciphertext_letters']}")
    print("    => Key Takeaway: Letter frequencies are flattened towards uniform, which hides the")
    print("       English distribution, but the cipher stays linear and falls to the attack below.")

    print(f"\n[4] KNOWN-PLAINTEXT ATTACK (KPA) SIMULATION:")
    known_prefix_len = 36
    known_prefix = sample_message[:known_prefix_len]
    print(f"    - Intercepted Ciphertext Length: {len(ciphertext)} chars")
    print(f"    - Known Plaintext Segment (First {known_prefix_len} chars):")
    print(f"      \"{known_prefix}\"")
    print("    - Vigenere key length treated as unknown (searching from 10 upward)")
    print("    - Launching algebraic periodic constraint cryptanalysis...")

    attack_res = KnownPlaintextAttacker.attack(
        ciphertext=ciphertext,
        known_prefix=known_prefix
    )

    if attack_res["success"]:
        print(f"    [+] ATTACK SUCCEEDED in {attack_res['elapsed_seconds'] * 1000.0:.3f} ms!")
        print(f"    [+] Matrices Evaluated: {attack_res['matrices_evaluated']}")
        print(f"    [+] Recovered 2x2 Hill Matrix: {attack_res['recovered_hill_mat']}")
        print(f"    [+] Recovered Key Length     : {attack_res['recovered_key_len']}")
        print(f"    [+] Recovered Vigenere Key   : '{attack_res['recovered_vigenere_key']}'")
        print(f"    [+] Full Plaintext Message Recovered:")
        print(f"        \"{attack_res['recovered_full_plaintext']}\"")
        exact_recovery = (attack_res['recovered_full_plaintext'] == sample_message)
        print(f"    [+] Full Message Exact Match: {exact_recovery}")
    else:
        print("    [-] Attack failed to find consistent key within limits.")

    print(f"\n[5] RUNNING EMPIRICAL BENCHMARKS:")
    benchmark_ciphers()
    benchmark_attack(trials=3)


def interactive_menu():
    print_banner()
    while True:
        print("\nMain Menu:")
        print("  1. Run Complete Automated Walkthrough (Recommended)")
        print("  2. Encrypt & Decrypt Custom Text")
        print("  3. Run Known-Plaintext Attack on Custom Message")
        print("  4. Run Performance & Complexity Benchmarks")
        print("  5. Decrypt a Ciphertext")
        print("  6. Exit")
        choice = input("\nEnter choice (1-6): ").strip()

        if choice == "1":
            run_full_walkthrough()
        elif choice == "2":
            vig_key = input("Enter Vigenere Key (>=10 chars) [Default: CRYPTOGRAPHYKEY]: ").strip() or "CRYPTOGRAPHYKEY"
            hill_key = input("Enter Hill Key Phrase (>=10 chars) [Default: HILLCIPHERKEY]: ").strip() or "HILLCIPHERKEY"
            try:
                c = CustomHybridCipher(vig_key, hill_key)
                text = input("Enter plaintext to encrypt: ").strip()
                if not text:
                    print("Empty input!")
                    continue
                ct = c.encrypt(text)
                print(f"\nCiphertext: {ct}")
                dt = c.decrypt(ct)
                print(f"Decrypted : {dt}")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "3":
            vig_key = input("Enter Vigenere Key (>=10 chars) [Default: SECURITYPROTOCOL]: ").strip() or "SECURITYPROTOCOL"
            hill_key = input("Enter Hill Key Phrase (>=10 chars) [Default: HILLCIPHERKEY]: ").strip() or "HILLCIPHERKEY"
            try:
                c = CustomHybridCipher(vig_key, hill_key)
                text = input("Enter target plaintext (>= 50 chars): ").strip()
                if len(clean_text(text)) < 40:
                    print("Please enter a longer message (at least 40 alphabetic characters)!")
                    continue
                ct = c.encrypt(text)
                print(f"Ciphertext: {ct}")
                known_len = int(input(f"Enter known prefix length (needs key length + 20) [Default: 36]: ").strip() or "36")
                known_p = clean_text(text)[:known_len]
                print(f"Attacking with known prefix: '{known_p}'...")
                res = KnownPlaintextAttacker.attack(ct, known_p)
                if res["success"]:
                    print(f"\n[+] Recovered Hill Matrix: {res['recovered_hill_mat']}")
                    print(f"[+] Recovered Vigenere Key: {res['recovered_vigenere_key']}")
                    print(f"[+] Recovered Plaintext: {res['recovered_full_plaintext']}")
                    print(f"[+] Time: {res['elapsed_seconds'] * 1000:.2f} ms")
                else:
                    print("[-] Attack unsuccessful.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "4":
            benchmark_ciphers()
            benchmark_attack(trials=3)
        elif choice == "5":
            vig_key = input("Enter Vigenere Key (>=10 chars): ").strip()
            hill_key = input("Enter Hill Key Phrase (>=10 chars): ").strip()
            try:
                c = CustomHybridCipher(vig_key, hill_key)
                print(f"Plaintext: {c.decrypt(input('Enter ciphertext: ').strip())}")
            except ValueError as e:
                print(f"Error: {e}")
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please select 1-6.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print_banner()
        run_full_walkthrough()
    else:
        interactive_menu()
