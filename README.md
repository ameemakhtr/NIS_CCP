# Network and Information Security (CT-486)
## Complex Computing Problem [CLO3]
### Design and Break a Custom Cipher Based on Classical Techniques

**Author:** Group Submission (Max 4 Members)  
**Course Code:** CT-486  
**Language:** Python 3.8+ (Tested on Python 3.14)

---

## 📌 Executive Summary
This repository contains the design, implementation, cryptanalysis, and empirical performance evaluation of a **Two-Stage Custom Hybrid Classical Cipher**. The cipher combines two fundamental classical cryptographic techniques:
1. **Stage 1 (Confusion):** Polyalphabetic Substitution (Vigenère Cipher) using a key of length $\ge 10$ characters.
2. **Stage 2 (Diffusion):** Permutation (Keyed Columnar Transposition Cipher) using a key of length $\ge 10$ characters.

The project demonstrates:
- Full mathematical formulation and implementation of encryption and decryption.
- Statistical resistance to monographic frequency analysis (demonstrated via Index of Coincidence $\approx 0.040$).
- Simulated cryptanalytic attack via a **Known-Plaintext Attack (KPA)** utilizing constraint-guided branch-and-bound solving to recover the transposition matrix, the Vigenère keyword, and decrypt the entire unknown message with **100% success rate**.
- Empirical benchmarking against the single-stage **Shift (Caesar) Cipher**.

---

## 📂 Project Architecture

```
NIS_CCP/
│
├── custom_cipher.py    # Core encryption/decryption logic & ShiftCipher baseline
├── attack.py           # Frequency analyzer, IoC calculator & KPA solver
├── benchmark.py        # Latency, throughput, and attack effort evaluation
├── test_suite.py       # Unit test suite for validation & edge cases
├── main.py             # Interactive CLI & automated demonstration walkthrough
├── REPORT.md           # Comprehensive Academic & Technical Report
└── README.md           # Setup and execution guide
```

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.8 or higher. No external libraries required (uses Python standard library).

### 2. Run Automated Walkthrough
To run the automated end-to-end demonstration (Encryption, Decryption, Frequency Analysis, Attack Simulation, and Benchmarking):
```bash
python main.py --demo
```

### 3. Run Interactive Console
```bash
python main.py
```
From the interactive menu:
- `1`: Run Complete Automated Walkthrough
- `2`: Encrypt & Decrypt Custom Text
- `3`: Run Known-Plaintext Attack on Custom Message
- `4`: Run Performance & Complexity Benchmarks
- `5`: Exit

### 4. Run Unit Tests
```bash
python test_suite.py
```

### 5. Run Standalone Benchmarks
```bash
python benchmark.py
```

---

## 📊 Summary of Results

| Metric | Single-Stage Shift Cipher | Custom Hybrid Cipher |
| :--- | :--- | :--- |
| **Technique** | Monoalphabetic Substitution | Polyalphabetic Substitution + Columnar Transposition |
| **Key Length** | 1 integer ($0 \le k < 26$) | Dual keys $\ge 10$ characters each |
| **Index of Coincidence ($IC$)** | $0.0655$ (High vulnerability) | $0.0400$ (Near uniform random distribution) |
| **Encryption Time ($N=10,000$)** | $2.58\text{ ms}$ | $5.68\text{ ms}$ ($O(N)$ linear complexity) |
| **KPA Recovery Time ($N=1,000$)** | $< 0.01\text{ ms}$ | $1.52\text{ ms}$ ($100\%$ recovery rate) |

For comprehensive theoretical foundations, algorithm steps, security proofs, and recommendations, see [REPORT.md](REPORT.md).
