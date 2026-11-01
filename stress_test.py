"""
Stress and Torture Test Suite
Tests random keys, edge cases, random plaintexts, and blind KPA recovery.
"""

import random
import string
from custom_cipher import CustomHybridCipher, clean_text
from attack import KnownPlaintextAttacker, FrequencyAnalyzer

print("=== STARTING FULL RIGOROUS STRESS TESTING ===")

# Test 1: Random keys and random messages round-trip
for trial in range(30):
    k_v_len = random.randint(10, 25)
    k_h_len = random.randint(10, 25)
    msg_len = random.randint(2, 500)

    k_v = "".join(random.choices(string.ascii_letters, k=k_v_len))
    k_h = "".join(random.choices(string.ascii_letters, k=k_h_len))
    msg = "".join(random.choices(string.ascii_letters + " 0123456789!@#$%^&*()_+-=", k=msg_len))

    c = CustomHybridCipher(k_v, k_h)
    ct = c.encrypt(msg)
    pt = c.decrypt(ct)

    expected = clean_text(msg)
    if len(expected) % 2 != 0:
        expected += "X"
    assert pt == expected, f"Trial {trial} failed!"

print("[+] 30/30 Random key/message round-trip stress tests PASSED!")

# Test 2: Edge Cases
print("\n=== TESTING EDGE CASES ===")
# Edge Case 1: Minimum length 2 characters
c = CustomHybridCipher("KEYFORTESTING123", "HILLKEYPHRASE456")
ct = c.encrypt("AB")
pt = c.decrypt(ct)
assert pt == "AB"
print("[+] Edge Case: 2 characters (minimal 1 block) PASSED!")

# Edge Case 2: Odd length (pads with X)
ct = c.encrypt("ABC")
pt = c.decrypt(ct)
assert pt == "ABCX"
print("[+] Edge Case: Odd length padding PASSED!")

# Edge Case 3: Empty string
assert c.encrypt("") == ""
assert c.decrypt("") == ""
print("[+] Edge Case: Empty string PASSED!")

# Edge Case 4: Long text (50,000 characters)
long_msg = "NEDUNIVERSITYDEPARTMENTOFCOMPUTERSCIENCEANDIT" * 1000
ct_long = c.encrypt(long_msg)
pt_long = c.decrypt(ct_long)
assert pt_long == long_msg
print("[+] Edge Case: 45,000 characters high-volume stress PASSED!")

# Test 3: Known-Plaintext Attack across multiple random scenarios
print("\n=== TESTING ATTACK RESILIENCE ACROSS SCENARIOS ===")
words = ["ATTACK", "DEFENSE", "NETWORK", "SECURITY", "SYSTEM", "ALGORITHM", "COMPUTER", "INTEGRITY", "CONFIDENTIALITY"]
for a_trial in range(5):
    k_v = "".join(random.choices(string.ascii_uppercase, k=random.randint(11, 15)))
    k_h = "".join(random.choices(string.ascii_uppercase, k=random.randint(11, 16)))

    msg = "".join(random.choices(words, k=25))  # ~150-200 chars
    cipher = CustomHybridCipher(k_v, k_h)
    ct = cipher.encrypt(msg)

    known_prefix = msg[:36]
    res = KnownPlaintextAttacker.attack(ct, known_prefix, len(k_v))

    expected = msg if len(msg) % 2 == 0 else msg + "X"
    assert res["success"] is True, f"Attack failed on trial {a_trial}!"
    assert res["recovered_full_plaintext"] == expected, f"Plaintext mismatch on trial {a_trial}!"
    print(f"    [+] Trial {a_trial + 1}: Success in {res['elapsed_seconds'] * 1000.0:.1f} ms (Recovered: {res['recovered_vigenere_key']})")

print("\n>>> ALL TESTS & VERIFICATIONS PASSED WITH 100% SUCCESS RATE! <<<")
