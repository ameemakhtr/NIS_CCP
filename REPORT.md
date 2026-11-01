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
3.     P_clean <- P_clean + 'X'  // Pad to even length for 2x1 block processing
4. End If
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
15. Return concatenated string of P_chars
```

---

## 3. Security Analysis of the Custom Cipher

### 3.1 Confusion and Diffusion
* **Confusion:** The polyalphabetic substitution eliminates monoalphabetic 1-to-1 character mappings. A frequent letter like `'E'` in English ($12.7\%$) maps to different ciphertext letters depending on the key position.
* **Diffusion:** The $2 \times 2$ Hill matrix transformation blends adjacent letter pairs. A modification in a single plaintext character alters both characters in the output block.

### 3.2 Statistical and Frequency Analysis
The **Index of Coincidence (IoC)** measures non-uniformity in character distributions:
$$IC = \frac{\sum_{i=A}^Z f_i (f_i - 1)}{N(N - 1)}$$
* Standard English Plaintext: $IC \approx 0.0667$
* Single-Stage Shift (Caesar) Cipher: $IC = 0.0655$ (Frequency distribution completely leaked)
* Uniform Random / Polyalphabetic Baseline: $IC \approx 0.0385$
* **Custom Hybrid Cipher:** $IC = \mathbf{0.0405}$

The cipher depresses the Index of Coincidence to near-random distribution ($0.0405$), rendering simple ciphertext-only frequency analysis attacks ineffective.

---

## 4. Description of Attack Methods and Results

Per the requirements, an attack program was implemented using a **Known-Plaintext Attack (KPA)** scenario.

### 4.1 Attack Scenario and Methodology
* **Assumed Attacker Access:** The adversary has intercepted the full ciphertext $C$ and possesses a known segment of the plaintext (first 36 characters) from standard message formats or headers.
* **Attack Method:**
  1. The total search space of $2 \times 2$ invertible matrices over $\mathbb{Z}_{26}$ is $|GL(2, \mathbb{Z}_{26})| = 157,248$.
  2. For each candidate matrix $K_H$, the attack inverts the Hill stage for the known prefix:
     $$\begin{pmatrix} x_1 \\ x_2 \end{pmatrix} = K_H^{-1} \begin{pmatrix} y_1 \\ y_2 \end{pmatrix} \pmod{26}$$
  3. The implied Vigenère keystream is derived:
     $$K[i] = (x_i - P_{known}[i]) \pmod{26}$$
  4. **Periodicity Check:** The Vigenère key must satisfy $K[i] \equiv K[i + L_V]$. Candidate matrices violating this periodicity are rejected immediately.
  5. The unique valid matrix and Vigenère keyword are extracted, allowing full decryption of the remaining ciphertext.

---

### 4.2 Attack Success Rate and Computational Effort

| Ciphertext Length ($N$) | Known Plaintext Characters ($M$) | Success Rate | Average Time (ms) | Candidate Matrices Evaluated |
| :---: | :---: | :---: | :---: | :---: |
| **100** | 36 | **100.0%** | **83.1 ms** | 42,881 |
| **250** | 36 | **100.0%** | **83.1 ms** | 42,881 |
| **500** | 36 | **100.0%** | **84.2 ms** | 42,881 |
| **1000** | 36 | **100.0%** | **84.0 ms** | 42,881 |

* **Success Rate:** $100\%$ across all tested lengths.
* **Computational Effort:** The attack evaluates candidate matrices in less than **$85\text{ milliseconds}$** on standard hardware, fully recovering both keys and the unknown plaintext.

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

| Length ($N$ characters) | Custom Encrypt (ms) | Custom Decrypt (ms) | Shift Encrypt (ms) | Shift Decrypt (ms) | Overhead Factor |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **100** | 0.0300 ms | 0.0300 ms | 0.0126 ms | 0.0126 ms | $\approx 2.38\times$ |
| **500** | 0.1426 ms | 0.1486 ms | 0.0601 ms | 0.0611 ms | $\approx 2.40\times$ |
| **1,000** | 0.2831 ms | 0.2940 ms | 0.1183 ms | 0.1198 ms | $\approx 2.45\times$ |
| **5,000** | 1.3792 ms | 1.4353 ms | 0.5583 ms | 0.5682 ms | $\approx 2.50\times$ |
| **10,000** | 2.8358 ms | 2.9351 ms | 1.1191 ms | 1.1346 ms | $\approx 2.55\times$ |

* **Analysis:** Both algorithms scale linearly with message size. The Custom Hybrid Cipher incurs an expected $\approx 2.4\times$ computational overhead over the single-stage Shift cipher due to the two sequential mathematical passes, while maintaining high throughput ($> 3.4\text{ million characters/sec}$).

---

## 6. Suggestions for Improving the Cipher's Security

To enhance security without significantly increasing algorithmic complexity:

1. **Autokey Key Scheduling:**  
   Replace the periodic repeating Vigenère key with an **Autokey** mechanism where subsequent keystream values are drawn from the plaintext itself ($K[i] = P[i - L_V]$). This retains $O(N)$ linear complexity while eliminating the periodic keystream alignment exploited by the attack.
2. **Larger Matrix Dimensions ($3 \times 3$ or $4 \times 4$):**  
   Increasing the Hill block size to $m = 3$ or $m = 4$ expands the matrix key space to $1.6 \times 10^{12}$ and $8.6 \times 10^{21}$ possible matrices, making exhaustive algebraic search computationally infeasible while adding negligible matrix multiplication overhead.
3. **Non-Linear S-Box Substitution:**  
   Introduce a simple non-linear permutation lookup (S-Box) between stages to break the linear modular relationships over $\mathbb{Z}_{26}$.

---

## 7. Code Submission & Execution Details

All project source files are organized into a clean repository:
* `custom_cipher.py`: Cipher implementation and baseline Shift cipher.
* `attack.py`: Frequency analysis and Known-Plaintext Attack solver.
* `benchmark.py`: Empirical timing and complexity benchmarking suite.
* `test_suite.py`: Automated unit tests.
* `live_test.py`: Custom message live demonstration script.
* `main.py`: Interactive CLI application (`python main.py --demo`).

**Execution Command:**
```bash
python main.py --demo
```
