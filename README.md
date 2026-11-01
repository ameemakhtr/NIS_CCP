# Network and Information Security (CT-486)
## Complex Computing Problem [CLO3]
### Design and Break a Custom Cipher Based on Classical Techniques

**Instructor:** Dr. Shariq Mahmood Khan  
**Course Code:** CT-486  
**Language:** Python 3.8+ (Tested on Python 3.14)

---

## 📌 Syllabus Alignment
This custom cipher is designed directly using classical ciphers taught in the **NIS-Lectures (Dr. Shariq Mahmood Khan)**:
1. **Stage 1 (Confusion):** **Vigenère Cipher** (`3-Vigenere-Cipher.pdf`) - Polyalphabetic Substitution with key length $\ge 10$ characters.
2. **Stage 2 (Diffusion):** **Hill Cipher** (`7-Hill-Ciphers.pdf`) - Polygraphic Block Linear Algebraic Transformation ($2 \times 2$ invertible matrix modulo 26 derived from key phrase $\ge 10$ characters).
3. **Comparative Baseline:** **Shift (Caesar) Cipher** (`2-Shift-Cipher.pdf`) - Single-stage classical cipher.

---

## 📂 Project Architecture

```
NIS_CCP/
│
├── custom_cipher.py    # Vigenere + Hill Hybrid Cipher & Shift Cipher baseline
├── attack.py           # Frequency analysis & Known-Plaintext Attack (KPA) solver
├── benchmark.py        # Latency, throughput, and attack effort evaluation
├── test_suite.py       # Unit test suite for validation & edge cases
├── main.py             # Interactive CLI & automated demonstration walkthrough
├── REPORT.md           # Comprehensive Academic & Technical Report
└── README.md           # Setup and execution guide
```

---

## 🚀 Quick Start Guide

### 1. Run Automated Demonstration
```bash
python main.py --demo
```

### 2. Run Interactive Console
```bash
python main.py
```

### 3. Run Unit Tests
```bash
python test_suite.py
```

### 4. Run Benchmarks
```bash
python benchmark.py
```

---

## 📊 Summary of Results

| Metric | Single-Stage Shift Cipher (`2-Shift`) | Custom Hybrid Cipher (`3-Vigenere` + `7-Hill`) |
| :--- | :--- | :--- |
| **Technique** | Monoalphabetic Substitution | Polyalphabetic Substitution + Polygraphic Block Transformation |
| **Key Requirements** | 1 integer ($0 \le k < 26$) | Dual keys $\ge 10$ characters each |
| **Index of Coincidence ($IC$)** | $0.06552$ (Vulnerable to frequency analysis) | **$0.03721$** (Near uniform random distribution $\approx 0.0385$) |
| **Encryption Time ($N=10,000$)** | $2.47\text{ ms}$ | $6.47\text{ ms}$ ($O(N)$ linear complexity) |
| **KPA Recovery Time ($N=1,000$)** | $< 0.01\text{ ms}$ | **$342.77\text{ ms}$** ($100\%$ message recovery rate) |

For complete mathematical derivations, pseudocode, and references, see [REPORT.md](REPORT.md).
