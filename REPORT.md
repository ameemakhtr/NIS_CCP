# Network and Information Security (CT-486)
## Complex Computing Problem [CLO3]
### Design and Break a Custom Cipher Based on Classical Techniques

**Course Code:** CT-486  
**Total Marks:** 10  
**Max Group Members:** 04  
**Submission Deadline:** 8th November 2026  

---

## 1. Combination of Classical Techniques to Form the Custom Cipher

Per the design requirements, the custom cipher combines two distinct classical cipher techniques studied in class into a two-stage product cipher:

1. **Stage 1: Polyalphabetic Substitution (Vigenère Cipher)**
   * **Technique:** Periodic shifting using a keyword of length $\ge 10$ characters (e.g., `CRYPTOGRAPHYKEY`, length 15).
   * **Purpose (Confusion):** Masks the predictable single-letter frequency distribution of English text. Each plaintext letter $P[i]$ is mapped to a different ciphertext letter depending on its position:
     $$C_1[i] = (P[i] + K_V[i \pmod{L_V}]) \pmod{26}$$

2. **Stage 2: Polygraphic Block Transformation (Hill Cipher)**
   * **Technique:** Linear algebraic block matrix multiplication over $\mathbb{Z}_{26}$ using a $2 \times 2$ invertible key matrix $K_H$ derived from a key phrase of length $\ge 10$ characters (e.g., `HILLCIPHERKEY`, length 13).
   * **Purpose (Diffusion):** Spreads statistical patterns across adjacent characters. Consecutive letters $(x_1, x_2)$ are transformed into $(y_1, y_2)$ via matrix multiplication:
     $$\begin{pmatrix} y_1 \\ y_2 \end{pmatrix} = \begin{pmatrix} a & b \\ c & d \end{pmatrix} \begin{pmatrix} x_1 \\ x_2 \end{pmatrix} \pmod{26}$$
     where $\gcd(\det(K_H), 26) = \gcd((ad - bc) \pmod{26}, 26) = 1$.

```
Plaintext (P) ──> [Stage 1: Vigenère Substitution] ──> Intermediate (C_1) ──> [Stage 2: Hill Block Matrix] ──> Ciphertext (C)
                     Key: K_V (length >= 10)                                     Key: K_H (2x2 Matrix, phrase >= 10)
```

---

## 2. Algorithms for Encryption and Decryption

### 2.1 Encryption Algorithm

```text
Algorithm 1: Custom Cipher Encryption
Input : Plaintext P, Vigenère Key K_V (length >= 10), Hill Key Matrix K_H (2x2)
Output: Ciphertext C

1. P_clean <- Filter uppercase A-Z characters from P
2. If Length(P_clean) mod 2 != 0 Then
3.     P_clean <- P_clean + 'X'  // Odd length: one padding letter
4. Else P_clean <- P_clean + 'XA'  // Even length: two, so padding is always removable
5. N <- Length(P_clean)
6. Initialize array C_1 of length N
7. For i <- 0 to N - 1 Do
8.     shift <- Ord(K_V[i mod Length(K_V)]) - 65
9.     C_1[i] <- (Ord(P_clean[i]) - 65 + shift) mod 26
10. End For
11. Initialize array C_nums of length N
12. For j <- 0 to (N / 2) - 1 Do
13.     x1 <- C_1[2*j], x2 <- C_1[2*j + 1]
14.     C_nums[2*j]     <- (K_H.a * x1 + K_H.b * x2) mod 26
15.     C_nums[2*j + 1] <- (K_H.c * x1 + K_H.d * x2) mod 26
16. End For
17. Return string of characters corresponding to C_nums
```

---

### 2.2 Decryption Algorithm

```text
Algorithm 2: Custom Cipher Decryption
Input : Ciphertext C, Vigenère Key K_V, Hill Key Matrix K_H
Output: Original Plaintext P

1. C_nums <- Convert uppercase A-Z characters of C to integers (0-25)
2. N <- Length(C_nums)
3. Compute K_inv <- (det(K_H))^-1 * [[d, -b], [-c, a]] mod 26
4. Initialize array C_1 of length N
5. For j <- 0 to (N / 2) - 1 Do
6.     y1 <- C_nums[2*j], y2 <- C_nums[2*j + 1]
7.     C_1[2*j]     <- (K_inv.a * y1 + K_inv.b * y2) mod 26
8.     C_1[2*j + 1] <- (K_inv.c * y1 + K_inv.d * y2) mod 26
9. End For
10. Initialize array P_chars of length N
11. For i <- 0 to N - 1 Do
12.     shift <- Ord(K_V[i mod Length(K_V)]) - 65
13.     P_chars[i] <- Chr(((C_1[i] - shift + 26) mod 26) + 65)
14. End For
15. If P_chars ends in 'X' remove 1 letter, otherwise remove 2 letters
16. Return concatenated string of P_chars
```

---

## 3. Security Analysis of the Custom Cipher

### 3.1 Confusion and Diffusion
* **Confusion:** The polyalphabetic substitution eliminates monoalphabetic 1-to-1 character mappings. A frequent letter like `'E'` in English ($12.7\%$) maps to different ciphertext letters depending on the key position.
* **Diffusion:** The $2 \times 2$ Hill matrix transformation blends adjacent letter pairs. Changing one plaintext letter changes at most its own output pair (measured average: 1.77 ciphertext letters), so diffusion is limited to one digram.

### 3.2 Statistical and Frequency Analysis
The **Index of Coincidence (IoC)** measures non-uniformity in character distributions:
$$IC = \frac{\sum_{i=A}^Z f_i (f_i - 1)}{N(N - 1)}$$
Measured over 30 random key sets and 5,000-letter passages of English technical documentation, which is slightly above the textbook 0.0667:

| Text | Mean IoC | Chi-squared vs English |
|---|:---:|:---:|
| Plaintext (English) | 0.0703 | 534.0 |
| Shift cipher | 0.0703 | 61,406.1 |
| Hill only | 0.0445 | 29,986.2 |
| Vigenere only | 0.0407 | 29,234.7 |
| **Custom (Vigenere + Hill)** | 0.0391 | 29,480.5 |

The Shift cipher keeps the plaintext's IoC exactly because it only renames letters. The custom cipher is close to the uniform value 0.0385 and its histogram no longer resembles English. Frequency analysis on its own does not recover the key, so it measures how well statistics are hidden; the cipher is broken by the attack in Section 4.

---

## 4. Description of Attack Methods and Results

Per the requirements, an attack program was implemented using a **Known-Plaintext Attack (KPA)** scenario.

### 4.1 Attack Scenario and Methodology
* **Assumed Attacker Access:** The adversary has the full ciphertext $C$ and its first $M$ letters of plaintext, for example a predictable header, and knows the algorithm but neither key nor the key length.
* **Attack Method:**
  1. For each key length $L_V$ from 10 to $M - 20$: the total search space of $2 \times 2$ invertible matrices over $\mathbb{Z}_{26}$ is $|GL(2, \mathbb{Z}_{26})| = 157,248$.
  2. For each candidate matrix $K_H$, the attack inverts the Hill stage for the known prefix:
     $$\begin{pmatrix} x_1 \\ x_2 \end{pmatrix} = K_H^{-1} \begin{pmatrix} y_1 \\ y_2 \end{pmatrix} \pmod{26}$$
  3. The implied Vigenère keystream is derived:
     $$K[i] = (x_i - P_{known}[i]) \pmod{26}$$
  4. **Periodicity Check:** The Vigenère key must satisfy $K[i] \equiv K[i + L_V]$. Candidate matrices violating this periodicity are rejected immediately.
  5. The unique valid matrix and Vigenère keyword are extracted, allowing full decryption of the remaining ciphertext.

---

### 4.2 Attack Success Rate and Computational Effort

Measured by `benchmark.py` (20 trials per row, new random keys and English text each trial; saved in `results.json`). The first 25% of each message is known, and success means the exact full message was recovered.

| Ciphertext length | Known letters | Success rate | Avg time (ms) | Worst time (ms) | Avg matrices tried |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 50 | 12 | 0.0% | 0.0 | 0.0 | 0 |
| 100 | 25 | 0.0% | 0.0 | 0.1 | 0 |
| 150 | 37 | 80.0% | 804.6 | 1742.5 | 650,590 |
| 200 | 50 | 100.0% | 1292.5 | 2339.3 | 934,022 |
| 500 | 125 | 100.0% | 1194.1 | 2307.1 | 862,325 |
| 1,000 | 250 | 100.0% | 1179.8 | 2817.9 | 866,487 |
| 5,000 | 1,250 | 100.0% | 1184.2 | 2440.0 | 822,389 |
| 10,000 | 2,500 | 100.0% | 1225.3 | 2735.2 | 866,181 |

| Known letters (1,000-letter ciphertext) | Success rate | Avg time (ms) |
| :---: | :---: | :---: |
| 20 | 0.0% | 0.2 |
| 30 | 0.0% | 208.9 |
| 34 | 25.0% | 880.3 |
| 36 | 65.0% | 1200.0 |
| 40 | 100.0% | 1105.9 |
| 50 | 100.0% | 1244.3 |
| 60 | 100.0% | 1502.4 |
| 100 | 100.0% | 1204.7 |

* **Known text needed:** Success depends on the amount of known text, which must be at least $L_V + 20$ letters. Because $26 = 2 \times 13$, a matrix wrong only mod 2 passes each check about half the time, so fewer extra letters return wrong keys.
* **Computational Effort:** When recovery succeeded the attack averaged about 1215 ms (worst 2818 ms), independent of ciphertext length, plus a one-off 350 ms to build the matrix pool.

---

## 5. Performance Metrics and Efficiency Considerations

### 5.1 Time Complexity Analysis
* **Encryption Time Complexity:**
  * Stage 1 (Vigenère): $O(N)$ operations for modular shifts.
  * Stage 2 (Hill): $O(N)$ operations ($N/2$ vector-matrix multiplications).
  * **Overall Custom Cipher:** $\mathbf{O(N)}$ linear time.
* **Decryption Time Complexity:**
  * Modular matrix inverse calculation: $O(1)$ constant time for $2 \times 2$ matrix.
  * Inverse Hill + Inverse Vigenère passes: $O(N)$.
  * **Overall Custom Cipher:** $\mathbf{O(N)}$ linear time.
* **Single-Stage Shift Cipher Comparison:** Shift cipher performs a single modular addition per character, running in $O(N)$ time.

---

### 5.2 Empirical Execution Benchmarks (50 Iteration Averages)

| Length | Custom encrypt (ms) | Custom decrypt (ms) | Shift encrypt (ms) | Shift decrypt (ms) | Encrypt overhead |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 100 | 0.0677 | 0.0508 | 0.0222 | 0.0225 | 3.05x |
| 500 | 0.2882 | 0.2871 | 0.1182 | 0.1176 | 2.44x |
| 1,000 | 0.4993 | 0.6358 | 0.2196 | 0.2153 | 2.27x |
| 5,000 | 2.4265 | 2.2959 | 1.0988 | 1.1122 | 2.21x |
| 10,000 | 4.7058 | 4.7004 | 2.5343 | 2.3451 | 1.86x |

* **Analysis:** Both algorithms scale linearly with message size. The two-stage cipher costs 1.9x to 3.0x the Shift cipher's time. Encrypting 1,000 letters took 0.499 ms against 0.220 ms.

---

## 6. Suggestions for Improving the Cipher's Security

The attack depends on linearity and on the repeating key, so useful changes must remove one of these. Each option stays $O(N)$. They were not implemented or measured here.

1. **Keyed Non-Linear Substitution:** Pass each Vigenère output letter through a secret permutation of the alphabet between the stages. $K[i] = x_i - P[i]$ then no longer holds, so the key cannot be read off after guessing the matrix.
2. **Keyed Columnar Transposition:** Reorder letters by a secret permutation between the stages, separating known plaintext from the ciphertext positions it produces.
3. **Non-Repeating Keystream:** Derive a different Vigenère key per message from the main key and a per-message value, so the periodicity check has nothing to test.

A longer Vigenère key only raises the known text needed. A larger Hill matrix alone leaves the system linear: subtracting blocks a whole number of key periods apart cancels the Vigenère term, giving $\Delta C = K_H \Delta P$, which linear algebra solves without search.

---

## 7. Code Submission & Execution Details

All project source files are hosted in the public GitHub repository:
**Repository Link:** https://github.com/ameemakhtr/NIS_CCP

### Repository Contents:
* `custom_cipher.py`: Cipher implementation and baseline Shift cipher.
* `attack.py`: Frequency analysis and Known-Plaintext Attack solver.
* `benchmark.py`: Empirical timing and attack benchmarks, written to `results.json`.
* `generate_plots.py`: Draws the figures from `results.json`.
* `test_suite.py`: Automated unit tests.
* `main.py`: Interactive CLI application (`python main.py --demo`).
* `build_report_pdf.py`: Academic PDF report generation engine.
* `Complex_Computing_Problem_Report.pdf`: Formal PDF report.

**Execution Command:**
```bash
python main.py --demo
```
