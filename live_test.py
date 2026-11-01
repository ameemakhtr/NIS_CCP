"""
Live demonstration script for custom message encryption, decryption, and cryptanalysis.
"""

from custom_cipher import CustomHybridCipher
from attack import KnownPlaintextAttacker

print("=" * 75)
print("     LIVE DEMO: CUSTOM CIPHER ENCRYPTION & ATTACK RECOVERY")
print("=" * 75)

# Keys (>= 10 characters)
v_key = "NEDUNIVERSITY"
h_key = "CYBERSECURITY"

cipher = CustomHybridCipher(v_key, h_key)
# Secret message with even length (76 chars)
secret_msg = "MEETATTHECAMPUSLIBRARYATTWOOCLOCKTOPREPAREFORNETWORKSECURITYVIVAEXAMINATIONS"

print("\n[1] Original Secret Plaintext:")
print("    " + secret_msg)

# Encrypt
ct = cipher.encrypt(secret_msg)
print("\n[2] Encrypted Ciphertext (Two-Stage: Vigenere + Hill):")
print("    " + ct)

# Decrypt
decrypted = cipher.decrypt(ct)
print("\n[3] Legitimate Receiver Decryption:")
print(f"    Decrypted: {decrypted}")
print(f"    Integrity Verified (Original == Decrypted): {decrypted == secret_msg}")

# Attack
known_part = secret_msg[:36]
print("\n[4] ATTACK SCENARIO (Known-Plaintext Attack):")
print("    Adversary intercepts the full ciphertext and only knows the first 36 letters:")
print(f"    Known Prefix: \"{known_part}\"")
print("    Attempting to crack secret keys and read the rest of the message...")

res = KnownPlaintextAttacker.attack(ct, known_part, len(v_key))

print("\n[5] ATTACK OUTCOME:")
print(f"    [+] Status                 : {'SUCCESS' if res['success'] else 'FAILED'}")
print(f"    [+] Time Taken to Crack    : {res['elapsed_seconds'] * 1000.0:.2f} ms")
print(f"    [+] Recovered Vigenere Key : '{res['recovered_vigenere_key']}'")
print(f"    [+] Recovered Hill Matrix  : {res['recovered_hill_mat']}")
print(f"    [+] Full Plaintext Cracked : {res['recovered_full_plaintext']}")
print(f"    [+] 100% Exact Match       : {res['recovered_full_plaintext'] == secret_msg}")
print("=" * 75)
