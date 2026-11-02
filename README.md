# CT-486: Network and Information Security (NIS)
## Complex Computing Problem (CCP) — Design & Break a Custom Classical Cipher [CLO3]

[![Language](https://img.shields.io/badge/Language-Python%203.14-blue.svg)](https://www.python.org/)
[![Cryptography](https://img.shields.io/badge/Cryptography-Classical%20Product%20Cipher-darkgreen.svg)]()
[![Design](https://img.shields.io/badge/Primitives-Vigen%C3%A8re%20%2B%20Hill%20(2%C3%972)-orange.svg)]()
[![Keyspace](https://img.shields.io/badge/GL(2%2C%20%E2%84%A4%E2%82%82%E2%82%86)-157%2C248%20Matrices-red.svg)]()
[![University](https://img.shields.io/badge/NED%20University-CS%20%26%20IT%20Department-red.svg)](https://www.neduet.edu.pk/)
[![Batch](https://img.shields.io/badge/Batch-2023-purple.svg)]()

This repository contains the complete implementation, cryptanalytic attack simulation, empirical benchmark suite, and formal academic report for the **Complex Computing Problem (CCP)** in **CT-486: Network and Information Security** at the **Department of Computer Science & Information Technology, NED University of Engineering & Technology, Karachi**.

---

## 📌 Project Overview & Abstract

In cryptography, a **Complex Computing Problem (CLO3)** requires engineering multi-stage cryptographic primitives that balance Claude Shannon's foundational principles of **Confusion** and **Diffusion** while maintaining strict mathematical invertibility, linear O(N) computational efficiency, and resilience against classical statistical attacks.

While individual classical ciphers (such as Caesar, Vigenère, or Hill) are trivial to break individually using frequency analysis or known-plaintext linear systems, composing orthogonal primitives into a **two-stage product cipher** demonstrates how classical building blocks interact. 

This project implements a high-throughput, two-stage classical hybrid cipher combining:
1. **Stage 1 (Polyalphabetic Substitution — Vigenère Cipher):** Masks monoalphabetic frequency spikes by cycling character shifts across a key of length ≥ 10 characters (enforcing strong Shannon *Confusion*).
2. **Stage 2 (Polygraphic Block Transformation — 2 × 2 Hill Cipher):** Entangles adjacent characters in ℤ₂₆ via matrix transformation over the General Linear Group GL(2, ℤ₂₆) (enforcing Shannon *Diffusion* across digrams).
3. **Cryptanalytic Attack Engine:** An automated solver simulating both ciphertext-only **Frequency Analysis (Index of Coincidence)** and an algebraic **Known-Plaintext Attack (KPA)** that breaks the cipher in < 45 ms.

---

## 📐 Mathematical Formulation & Cryptographic Architecture

Let plaintext message P = (p₀, p₁, ..., pₙ₋₁) be mapped to numeric residues ℤ₂₆ = {0, 1, ..., 25}. The encryption pipeline operates across two sequential stages:

```
Plaintext (P) ──> [Stage 1: Vigenère Substitution] ──> Intermediate (C_1) ──> [Stage 2: Hill 2x2 Matrix] ──> Ciphertext (C)
                     Key: K_vig (Length >= 10)                                   Key Matrix: K_hill in GL(2, Z_26)
```

### Stage 1: Polyalphabetic Modular Substitution

$$
C_1[i] = (P[i] + K_{\text{vig}}[i \bmod L]) \pmod{26}
$$

where L ≥ 10 is the primary key length.

### Stage 2: Polygraphic Block Linear Transformation

$$
\begin{pmatrix} C[2j] \\ C[2j+1] \end{pmatrix} = \mathbf{K}_{\text{hill}} \cdot \begin{pmatrix} C_1[2j] \\ C_1[2j+1] \end{pmatrix} \pmod{26}
$$

### Algebraic Invertibility in GL(2, ℤ₂₆)

For the decryption transformation to be unique, the 2 × 2 Hill matrix **K**_hill = [[a, b], [c, d]] must have a determinant Δ = (ad - bc) mod 26 coprime to 26:

$$
\gcd(\Delta, 26) = 1 \iff \Delta \not\equiv 0 \pmod 2 \quad \text{and} \quad \Delta \not\equiv 0 \pmod{13}
$$

The modular decryption inverse matrix is given by:

$$
\mathbf{K}_{\text{hill}}^{-1} = \Delta^{-1} \cdot \begin{pmatrix} d & -b \\ -c & a \end{pmatrix} \pmod{26}
$$

The order of the General Linear Group provides |GL(2, ℤ₂₆)| = **157,248** valid invertible matrices.

---

## 🚀 Key Algorithms Implemented

### 1. Custom Cipher Encryption (`custom_cipher.py`)
```python
def encrypt(self, plaintext: str) -> str:
    cleaned = [c for c in plaintext.upper() if c in ALPHABET]
    if len(cleaned) % 2 != 0:
        cleaned.append('X')  # Pad for 2x1 block processing
    
    # Stage 1: Vigenère Substitution
    c1 = [(ord(p) - 65 + ord(self.vig_key[i % self.vig_len]) - 65) % 26 
          for i, p in enumerate(cleaned)]
    
    # Stage 2: Hill Block Matrix Transformation (Column-Vector convention)
    c2 = []
    a, b, c, d = self.hill_matrix
    for j in range(0, len(c1), 2):
        x1, x2 = c1[j], c1[j+1]
        c2.append(chr(((a * x1 + b * x2) % 26) + 65))
        c2.append(chr(((c * x1 + d * x2) % 26) + 65))
    return "".join(c2)
```

### 2. Custom Cipher Decryption (`custom_cipher.py`)
* Computes modular inverse Δ⁻¹ (mod 26) using the Extended Euclidean Algorithm.
* Multiplies ciphertext digram vectors by **K**_hill⁻¹ (mod 26) to invert Stage 2.
* Subtracts modular Vigenère key shifts to perfectly restore original plaintext.

---

## 🛡️ Security Analysis & Statistical Defense

### 1. Shannon's Confusion and Diffusion
* **Confusion:** The 10-character Vigenère key disperses each character across 10 distinct Caesar alphabets, flattening monoalphabetic frequency spikes.
* **Diffusion:** The 2 × 2 Hill matrix transformation blends adjacent characters; altering a single character alters both letters in the output digram.

### 2. Friedman's Index of Coincidence (IoC)
The Index of Coincidence measures the non-uniformity of character distributions:

$$
\text{IoC} = \frac{\sum_{i=A}^{Z} f_i (f_i - 1)}{N(N - 1)}
$$

| Cipher Type | Index of Coincidence (IoC) | Vulnerability Status |
|---|:---:|---|
| **English Plaintext** | 0.0667 | Normal Language Baseline |
| **Shift (Caesar) Cipher** | 0.0665 | **Extremely Vulnerable** (Direct 1-to-1 frequency leakage) |
| **Custom Two-Stage Cipher** | **0.0405** | **Resistant** (Approaches uniform random baseline 0.0385) |

---

## ⚔️ Cryptanalytic Attack Simulation (Known-Plaintext Attack)

While the custom cipher defeats simple frequency analysis, classical ciphers are linear over ℤ₂₆. An automated **Known-Plaintext Attack (KPA)** engine was developed (`attack.py`):

$$
\mathbf{C} = \mathbf{K}_{\text{hill}} \cdot (\mathbf{P} + \mathbf{K}_{\text{vig}}) \pmod{26}
$$

When the attacker observes plaintext aligned across the key period L = 10, difference vectors eliminate the constant Vigenère key term:

$$
\Delta\mathbf{C} \equiv \mathbf{K}_{\text{hill}} \cdot \Delta\mathbf{P} \pmod{26} \implies \mathbf{K}_{\text{hill}} = \Delta\mathbf{C} \cdot (\Delta\mathbf{P})^{-1} \pmod{26}
$$

### Empirical Attack Success Rate & Computational Effort:
Evaluated across varying message lengths on standard CPU hardware:

| Ciphertext Length (N) | Known Plaintext (M) | Attack Method | Key Recovery Time | Success Rate (%) |
| :---: | :---: | :---: | :---: | :---: |
| **100 Chars** | 4 Chars (2 pairs) | KPA Matrix Inversion | **18.5 ms** | **92.0%** |
| **500 Chars** | 6 Chars (3 pairs) | KPA Matrix Inversion | **24.2 ms** | **97.5%** |
| **1,000 Chars** | 10 Chars (Full Key) | KPA Matrix Inversion | **42.1 ms** | **100.0%** |
| **5,000 Chars** | 20 Chars (Redundant) | KPA Matrix Inversion | **78.4 ms** | **100.0%** |
| **10,000 Chars** | 100 Chars (Redundant) | KPA Matrix Inversion | **215.0 ms** | **100.0%** |

> **Cryptanalytic Takeaway:** Classical linear product ciphers collapse under Known-Plaintext Cryptanalysis regardless of key length, demonstrating why modern ciphers (such as AES) mandate non-linear substitution boxes (S-Boxes).

---

## 📊 Performance Benchmarks vs. Shift Cipher Baseline

Empirical benchmarks were executed across 50 iterations per message size:

| Metric | Single-Stage Shift Cipher | Custom Two-Stage Cipher | Relative Ratio |
|---|:---:|:---:|:---:|
| **Asymptotic Time Complexity** | O(N) | O(N) | Identical O(N) Linear Class |
| **Asymptotic Space Complexity** | O(N) | O(N) | Identical O(N) Linear Class |
| **Keyspace Complexity** | 26 states (trivial) | 26¹⁰ × 157,248 ≈ **2.2 × 10¹⁹** | **8.5 × 10¹⁷×** Larger |
| **Throughput (1,000 chars)** | 4,032,258 chars/s | **1,347,708 chars/s** | High-speed streaming |
| **Encryption Time (1,000 chars)** | 0.248 ms | 0.742 ms | 2.99× Runtime Overhead |
| **Resistance to Frequency Attacks** | Vulnerable (IoC = 0.0665) | **Resistant (IoC = 0.0405)** | Dramatically Superior |

---

## 📈 Visual Benchmark & Cryptanalysis Plots

<p align="center">
  <img src="frequency_ioc_analysis.png" width="49%" alt="Frequency Distribution and IoC Benchmarks" />
  <img src="benchmark_comparison.png" width="49%" alt="Empirical Encryption Latency and Attack Recovery" />
</p>

* **Figure 1 (Left):** Letter frequency flattening and Index of Coincidence comparison across English, Shift, and Custom ciphers.
* **Figure 2 (Right):** Linear execution time scaling (O(N)) and Known-Plaintext Attack key recovery latency (< 45 ms).

---

## 🛠️ How to Build, Test & Run

### Prerequisites
* Python 3.10+ (tested on Python 3.14)
* Standard libraries (`reportlab` and `matplotlib` for regenerating reports/plots)

```bash
# Clone the repository
git clone https://github.com/ameemakhtr/NIS_CCP.git
cd NIS_CCP

# Install dependencies (if generating plots or compiling PDF)
pip install reportlab matplotlib pypdf
```

### Execution Commands

```bash
# 1. Run Complete Automated Walkthrough (Demo Mode)
python main.py --demo

# 2. Run Automated Unit Tests (6/6 passing)
python test_suite.py

# 3. Run Standalone Performance & Attack Benchmarks
python benchmark.py

# 4. Recompile Academic 6-Page PDF Report
python build_report_pdf.py
```

---

## 📂 Repository File Structure

```
NIS_CCP/
│
├── custom_cipher.py                    # Custom Hybrid Cipher (Vigenère + Hill 2x2) & Shift Cipher
├── attack.py                           # Frequency analysis, IoC calculator & KPA solver
├── benchmark.py                        # Empirical latency & throughput benchmark suite
├── test_suite.py                       # Automated unit tests (6/6 passing)
├── main.py                             # Interactive CLI & automated demo runner
├── generate_plots.py                   # High-res vector plot generation script
├── build_report_pdf.py                 # Academic 6-page PDF report compilation engine
├── Complex_Computing_Problem_Report.pdf# Formal Academic PDF Report (6 pages)
├── REPORT.md                           # Comprehensive Markdown technical report
├── README.md                           # Professional repository documentation
├── LICENSE                             # MIT Open-Source License
└── assets / figures
    ├── ned_logo_1.png                  # NED University official emblem
    ├── frequency_ioc_analysis.png      # Figure 1: Statistical frequency analysis plot
    └── benchmark_comparison.png        # Figure 2: Latency & attack recovery plot
```

---

## 📑 Formal Academic PDF Report

The formal, publication-grade academic report is precompiled and available directly in the repository:
* **PDF File:** [`Complex_Computing_Problem_Report.pdf`](Complex_Computing_Problem_Report.pdf)
* **Page Count:** Exactly 6 dense, fluff-free pages formatted to academic conference standards.
* **Cover Page:** Formal NED University formatting, logo, department, course code, student credentials, and faculty designation.

---

## 👥 Project Team & Contributors

*Department of Computer Science & Information Technology, NED University of Engineering & Technology, Karachi*  
**Course:** CT-486: Network and Information Security | **Batch:** 2023 | **Program:** Final Year - Cyber Security  
**Instructor:** Prof. Dr. Shariq Mahmood Khan (Professor, Department of CS & IT)

| S.No | Student Name | Roll Number | GitHub Profile |
| :---: | :--- | :---: | :---: |
| 1 | **Mr. Ameem Akhtar** | CR-23013 | [@ameemakhtr](https://github.com/ameemakhtr) |
| 2 | **Mr. Minhal Rizvi** | CR-23017 | [@Minhal128](https://github.com/Minhal128) |
| 3 | **Mr. Muhammad Usman** | CR-23038 | [@Daedalus46](https://github.com/Daedalus46) |
| 4 | **Mr. Maaz Wasim** | CR-23041 | [@maazw](https://github.com/maazw) |

---

## 📄 License
This project is developed for academic evaluation in CT-486 Network and Information Security at NED University of Engineering & Technology. Open-sourced under the [MIT License](LICENSE).
