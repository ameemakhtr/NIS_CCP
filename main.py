"""
Main Interactive Console Application
Course: Network and Information Security (CT-486)
CLO: Complex Computing Problem [CLO3]
Project: Design and Break a Custom Cipher Based on Classical Techniques
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
  [+] Stage 1: Polyalphabetic Substitution (Vigenere Cipher) - Confusion
  [+] Stage 2: Permutation (Keyed Columnar Transposition)   - Diffusion
  [+] Minimum Key Length: >= 10 characters
========================================================================
""")


def run_full_walkthrough():
    print("\n>>> EXECUTING AUTOMATED COMPREHENSIVE WALKTHROUGH <<<\n")

    sub_key = "CRYPTOGRAPHYKEY"   # 15 chars
    trans_key = "ALGORITHMIC"     # 11 chars
    print(f"[*] Initializing Custom Hybrid Cipher:")
    print(f"    - Substitution Key   (Stage 1) : '{sub_key}' (Length: {len(sub_key)})")
    print(f"    - Transposition Key  (Stage 2) : '{trans_key}' (Length: {len(trans_key)})")

    cipher = CustomHybridCipher(sub_key, trans_key)

    sample_message = (
        "CONFIDENTIALCOMMUNICATIONFORNETWORKSECURITYOFFICERS"
        "ALLRELAYSTATIONSMUSTTRANSITIONTOQUANTUMRESISTANTALGORITHMSBYTOMORROWEVENING"
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
    match = (decrypted == clean_text(sample_message))
    print(f"    Integrity Verification (Original == Decrypted): {match}")

    print(f"\n[3] STATISTICAL & FREQUENCY ANALYSIS:")
    stats = FrequencyAnalyzer.analyze(sample_message, ciphertext)
    print(f"    - Plaintext Index of Coincidence (IoC)  : {stats['plaintext_ioc']:.5f} (English Ref: ~0.0667)")
    print(f"    - Ciphertext Index of Coincidence (IoC) : {stats['ciphertext_ioc']:.5f} (Polyalphabetic/Random Ref: ~0.0385)")
    print(f"    - Plaintext Chi-Squared Statistic      : {stats['plaintext_chi_sq']:.2f}")
    print(f"    - Ciphertext Chi-Squared Statistic     : {stats['ciphertext_chi_sq']:.2f}")
    print(f"    - Top 5 Plaintext Letters              : {stats['top_plaintext_letters']}")
    print(f"    - Top 5 Ciphertext Letters             : {stats['top_ciphertext_letters']}")
    print("    => Key Takeaway: The hybrid cipher successfully flattens monographic frequencies,")
    print("       preventing direct single-letter substitution attacks.")

    print(f"\n[4] KNOWN-PLAINTEXT ATTACK (KPA) SIMULATION:")
    known_prefix_len = 35
    known_prefix = sample_message[:known_prefix_len]
    print(f"    - Intercepted Ciphertext Length: {len(ciphertext)} chars")
    print(f"    - Known Plaintext Segment (First {known_prefix_len} chars):")
    print(f"      \"{known_prefix}\"")
    print("    - Launching constraint-guided branch-and-bound cryptanalysis...")

    attack_res = KnownPlaintextAttacker.attack(
        ciphertext=ciphertext,
        known_prefix=known_prefix,
        trans_key_len=len(trans_key),
        sub_key_len=len(sub_key)
    )

    if attack_res["success"]:
        print(f"    [+] ATTACK SUCCEEDED in {attack_res['elapsed_seconds'] * 1000.0:.3f} ms!")
        print(f"    [+] Branches Evaluated: {attack_res['branch_evaluations']}")
        print(f"    [+] Recovered Substitution Key: '{attack_res['recovered_sub_key']}'")
        print(f"    [+] Full Plaintext Message Recovered:")
        print(f"        \"{attack_res['recovered_full_plaintext']}\"")
        exact_recovery = (attack_res['recovered_full_plaintext'] == sample_message)
        print(f"    [+] Full Message Exact Match: {exact_recovery}")
    else:
        print("    [-] Attack failed to find consistent key within limits.")

    print(f"\n[5] RUNNING EMPIRICAL BENCHMARKS:")
    benchmark_ciphers()
    benchmark_attack()


def interactive_menu():
    print_banner()
    while True:
        print("\nMain Menu:")
        print("  1. Run Complete Automated Walkthrough (Recommended)")
        print("  2. Encrypt & Decrypt Custom Text")
        print("  3. Run Known-Plaintext Attack on Custom Message")
        print("  4. Run Performance & Complexity Benchmarks")
        print("  5. Exit")
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            run_full_walkthrough()
        elif choice == "2":
            sub_key = input("Enter Substitution Key (>=10 chars) [Default: CRYPTOGRAPHYKEY]: ").strip() or "CRYPTOGRAPHYKEY"
            trans_key = input("Enter Transposition Key (>=10 chars) [Default: ALGORITHMIC]: ").strip() or "ALGORITHMIC"
            try:
                c = CustomHybridCipher(sub_key, trans_key)
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
            sub_key = input("Enter Substitution Key (>=10 chars) [Default: SECURITYANALYSIS]: ").strip() or "SECURITYANALYSIS"
            trans_key = input("Enter Transposition Key (>=10 chars) [Default: PERMUTATION]: ").strip() or "PERMUTATION"
            try:
                c = CustomHybridCipher(sub_key, trans_key)
                text = input("Enter target plaintext (>= 50 chars): ").strip()
                if len(clean_text(text)) < 40:
                    print("Please enter a longer message (at least 40 alphabetic characters)!")
                    continue
                ct = c.encrypt(text)
                print(f"Ciphertext: {ct}")
                known_len = int(input(f"Enter known prefix length (suggested 30-40) [Default: 35]: ").strip() or "35")
                known_p = clean_text(text)[:known_len]
                print(f"Attacking with known prefix: '{known_p}'...")
                res = KnownPlaintextAttacker.attack(ct, known_p, len(clean_text(trans_key)), len(clean_text(sub_key)))
                if res["success"]:
                    print(f"\n[+] Recovered Key: {res['recovered_sub_key']}")
                    print(f"[+] Recovered Plaintext: {res['recovered_full_plaintext']}")
                    print(f"[+] Time: {res['elapsed_seconds'] * 1000:.2f} ms")
                else:
                    print("[-] Attack unsuccessful.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "4":
            benchmark_ciphers()
            benchmark_attack()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please select 1-5.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print_banner()
        run_full_walkthrough()
    else:
        interactive_menu()
