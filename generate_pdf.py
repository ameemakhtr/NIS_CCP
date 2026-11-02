"""
PDF Generation Script for NIS CT-486 Complex Computing Problem [CLO3] Report
Uses ReportLab to compile REPORT.md into a professional academic PDF document.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y' in the running footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Network and Information Security (CT-486) | Complex Computing Problem [CLO3]")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Design and Break a Custom Cipher Based on Classical Techniques")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(612 - 54, 32, page_str)
        self.restoreState()


def build_pdf(filename="REPORT.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=4,
        alignment=1  # Centered
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=12,
        alignment=1  # Centered
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4A5568"),
        alignment=1
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=14,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        fontName='Courier',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#1A202C")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
        alignment=1
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("Network and Information Security (CT-486)", subtitle_style))
    story.append(Paragraph("Complex Computing Problem [CLO3]", subtitle_style))
    story.append(Paragraph("Design and Break a Custom Cipher Based on Classical Techniques", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Course Code:</b> CT-486 &nbsp;|&nbsp; <b>Total Marks:</b> 10 &nbsp;|&nbsp; <b>Max Group Members:</b> 04 &nbsp;|&nbsp; <b>Submission Deadline:</b> 8th November 2026", meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceAfter=12))

    # Section 1
    story.append(Paragraph("1. Combination of Classical Techniques to Form the Custom Cipher", h1_style))
    story.append(Paragraph(
        "Per the project specification, the custom cipher is designed as a two-stage hybrid product cipher combining two distinct classical techniques studied in class:",
        body_style
    ))
    story.append(Paragraph(
        "&bull; <b>Stage 1: Polyalphabetic Substitution (Vigenère Cipher):</b> Periodic key shifting using a secret keyword of length &ge; 10 characters (e.g., <code>CRYPTOGRAPHYKEY</code>, length 15). It achieves Claude Shannon's principle of <i>Confusion</i> by breaking monoalphabetic letter frequencies. Each character is shifted: <code>C_1[i] = (P[i] + K_V[i mod L_V]) mod 26</code>.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Stage 2: Polygraphic Block Transformation (Hill Cipher):</b> Linear algebraic 2x2 matrix multiplication over &Zopf;<sub>26</sub> using an invertible key matrix <code>K_H</code> derived from a key phrase of length &ge; 10 characters (e.g., <code>HILLCIPHERKEY</code>, length 13). It achieves <i>Diffusion</i> by mixing adjacent letter pairs <code>(x1, x2)</code> into <code>(y1, y2)</code> such that gcd(det(K_H), 26) = 1.",
        bullet_style
    ))
    story.append(Spacer(1, 4))

    # Architecture Box
    diag_text = (
        "  Plaintext (P) ──> [Stage 1: Vigenere Substitution] ──> Intermediate (C_1) ──> [Stage 2: Hill Block Matrix] ──> Ciphertext (C)\n"
        "                       Key: K_V (length >= 10)                                       Key: K_H (2x2 Matrix, phrase >= 10)"
    )
    diag_table = Table([[Paragraph(f"<pre>{diag_text}</pre>", code_style)]], colWidths=[504])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 10))

    # Section 2
    story.append(Paragraph("2. Algorithms for Encryption and Decryption", h1_style))
    story.append(Paragraph("2.1 Encryption Algorithm", h2_style))

    enc_code = (
        "Algorithm 1: Custom Cipher Encryption\n"
        "Input : Plaintext P, Vigenere Key K_V (length >= 10), Hill Key Matrix K_H (2x2)\n"
        "Output: Ciphertext C\n\n"
        "1. P_clean <- Filter uppercase A-Z characters from P\n"
        "2. If Length(P_clean) mod 2 != 0 Then P_clean <- P_clean + 'X'  // Pad for 2x1 blocks\n"
        "3. N <- Length(P_clean), Initialize array C_1 of length N\n"
        "4. For i <- 0 to N - 1 Do\n"
        "5.     shift <- Ord(K_V[i mod Length(K_V)]) - 65\n"
        "6.     C_1[i] <- (Ord(P_clean[i]) - 65 + shift) mod 26\n"
        "7. End For\n"
        "8. Initialize array C_nums of length N\n"
        "9. For j <- 0 to (N / 2) - 1 Do\n"
        "10.    x1 <- C_1[2*j], x2 <- C_1[2*j + 1]\n"
        "11.    C_nums[2*j]     <- (K_H.a * x1 + K_H.b * x2) mod 26\n"
        "12.    C_nums[2*j + 1] <- (K_H.c * x1 + K_H.d * x2) mod 26\n"
        "13. End For\n"
        "14. Return string of characters corresponding to C_nums"
    )
    enc_table = Table([[Paragraph(f"<pre>{enc_code}</pre>", code_style)]], colWidths=[504])
    enc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(enc_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2.2 Decryption Algorithm", h2_style))
    dec_code = (
        "Algorithm 2: Custom Cipher Decryption\n"
        "Input : Ciphertext C, Vigenere Key K_V, Hill Key Matrix K_H\n"
        "Output: Original Plaintext P\n\n"
        "1. C_nums <- Convert uppercase A-Z characters of C to integers (0-25), N <- Length(C_nums)\n"
        "2. Compute K_inv <- (det(K_H))^-1 * [[d, -b], [-c, a]] mod 26\n"
        "3. Initialize array C_1 of length N\n"
        "4. For j <- 0 to (N / 2) - 1 Do\n"
        "5.     y1 <- C_nums[2*j], y2 <- C_nums[2*j + 1]\n"
        "6.     C_1[2*j]     <- (K_inv.a * y1 + K_inv.b * y2) mod 26\n"
        "7.     C_1[2*j + 1] <- (K_inv.c * y1 + K_inv.d * y2) mod 26\n"
        "8. End For\n"
        "9. Initialize array P_chars of length N\n"
        "10. For i <- 0 to N - 1 Do\n"
        "11.    shift <- Ord(K_V[i mod Length(K_V)]) - 65\n"
        "12.    P_chars[i] <- Chr(((C_1[i] - shift + 26) mod 26) + 65)\n"
        "13. End For\n"
        "14. Return concatenated string of P_chars"
    )
    dec_table = Table([[Paragraph(f"<pre>{dec_code}</pre>", code_style)]], colWidths=[504])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(dec_table)
    story.append(Spacer(1, 10))

    # Section 3
    story.append(Paragraph("3. Security Analysis of the Custom Cipher", h1_style))
    story.append(Paragraph(
        "<b>Confusion & Diffusion Assessment:</b> The Vigenère stage prevents direct single-letter frequency leakage (such as English letter 'E' at 12.7%). Simultaneously, the Hill stage spreads the statistical profile across adjacent character pairs. Modifying a single character alters two output symbols, ensuring strong diffusion.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Index of Coincidence (IoC) Cryptanalysis:</b> The Index of Coincidence measures the probability that two randomly selected letters from the text are identical: <code>IC = &Sigma; f_i(f_i - 1) / (N(N - 1))</code>.",
        body_style
    ))

    ioc_data = [
        [Paragraph("<b>Text / Cipher Sample</b>", table_header_style), Paragraph("<b>Observed Index of Coincidence (IC)</b>", table_header_style), Paragraph("<b>Vulnerability Status</b>", table_header_style)],
        [Paragraph("Standard English Plaintext", table_cell_style), Paragraph("0.0667 (Expected)", table_cell_style), Paragraph("Natural language baseline", table_cell_style)],
        [Paragraph("Single-Stage Shift (Caesar) Cipher", table_cell_style), Paragraph("0.0655", table_cell_style), Paragraph("Highly Vulnerable (Exact frequency preserved)", table_cell_style)],
        [Paragraph("Uniform Random / Polyalphabetic Target", table_cell_style), Paragraph("0.0385", table_cell_style), Paragraph("Theoretical ideal random spread", table_cell_style)],
        [Paragraph("<b>Custom Hybrid Cipher (Vigenère + Hill)</b>", table_cell_bold), Paragraph("<b>0.0405</b>", table_cell_bold), Paragraph("<b>Resistant to monographic frequency attacks</b>", table_cell_bold)],
    ]
    ioc_table = Table(ioc_data, colWidths=[174, 150, 180])
    ioc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(ioc_table)
    story.append(Spacer(1, 10))

    # Section 4
    story.append(Paragraph("4. Description of Attack Methods and Results", h1_style))
    story.append(Paragraph(
        "<b>Threat Model:</b> An adversary intercepts full ciphertext C and possesses a known plaintext prefix (first 36 characters) from standard application headers. The goal is to recover both keys and decrypt the entire remaining ciphertext.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Attack Algorithm:</b> The search space of 2x2 invertible matrices modulo 26 is |GL(2, &Zopf;<sub>26</sub>)| = 157,248. The attacker iterates through candidate matrices, partially inverting the Hill stage on the known prefix: <code>[x1, x2]^T = K_H^-1 * [y1, y2]^T mod 26</code>. The candidate Vigenère key stream <code>K[i] = (x_i - P_known[i]) mod 26</code> must strictly satisfy periodicity <code>K[i] == K[i + L_V]</code>. Inconsistent matrices are pruned instantly, isolating the exact Hill matrix and Vigenère key in milliseconds.",
        body_style
    ))

    attack_data = [
        [Paragraph("<b>Ciphertext Length (N)</b>", table_header_style), Paragraph("<b>Known Chars (M)</b>", table_header_style), Paragraph("<b>Success Rate</b>", table_header_style), Paragraph("<b>Avg Attack Time (ms)</b>", table_header_style), Paragraph("<b>Candidate Matrices Evaluated</b>", table_header_style)],
        [Paragraph("100 chars", table_cell_style), Paragraph("36", table_cell_style), Paragraph("100.0%", table_cell_style), Paragraph("83.1 ms", table_cell_style), Paragraph("42,881", table_cell_style)],
        [Paragraph("250 chars", table_cell_style), Paragraph("36", table_cell_style), Paragraph("100.0%", table_cell_style), Paragraph("83.1 ms", table_cell_style), Paragraph("42,881", table_cell_style)],
        [Paragraph("500 chars", table_cell_style), Paragraph("36", table_cell_style), Paragraph("100.0%", table_cell_style), Paragraph("84.2 ms", table_cell_style), Paragraph("42,881", table_cell_style)],
        [Paragraph("1,000 chars", table_cell_style), Paragraph("36", table_cell_style), Paragraph("100.0%", table_cell_style), Paragraph("84.0 ms", table_cell_style), Paragraph("42,881", table_cell_style)],
    ]
    attack_table = Table(attack_data, colWidths=[95, 85, 95, 110, 119])
    attack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(attack_table)
    story.append(Spacer(1, 10))

    # Section 5
    story.append(Paragraph("5. Performance Metrics and Efficiency Considerations", h1_style))
    story.append(Paragraph(
        "<b>Asymptotic Time Complexity:</b><br/>"
        "&bull; <b>Custom Hybrid Encryption/Decryption:</b> O(N) linear time (Stage 1 takes O(N) operations; Stage 2 processes N/2 blocks of size 2x2 taking O(1) per block, total O(N)).<br/>"
        "&bull; <b>Baseline Shift Cipher:</b> O(N) linear time (single modular shift per character).",
        body_style
    ))

    bench_data = [
        [Paragraph("<b>Message Length (N)</b>", table_header_style), Paragraph("<b>Custom Enc (ms)</b>", table_header_style), Paragraph("<b>Custom Dec (ms)</b>", table_header_style), Paragraph("<b>Shift Enc (ms)</b>", table_header_style), Paragraph("<b>Shift Dec (ms)</b>", table_header_style), Paragraph("<b>Overhead Factor</b>", table_header_style)],
        [Paragraph("100 chars", table_cell_style), Paragraph("0.0300 ms", table_cell_style), Paragraph("0.0300 ms", table_cell_style), Paragraph("0.0126 ms", table_cell_style), Paragraph("0.0126 ms", table_cell_style), Paragraph("2.38x", table_cell_style)],
        [Paragraph("500 chars", table_cell_style), Paragraph("0.1426 ms", table_cell_style), Paragraph("0.1486 ms", table_cell_style), Paragraph("0.0601 ms", table_cell_style), Paragraph("0.0611 ms", table_cell_style), Paragraph("2.40x", table_cell_style)],
        [Paragraph("1,000 chars", table_cell_style), Paragraph("0.2831 ms", table_cell_style), Paragraph("0.2940 ms", table_cell_style), Paragraph("0.1183 ms", table_cell_style), Paragraph("0.1198 ms", table_cell_style), Paragraph("2.45x", table_cell_style)],
        [Paragraph("5,000 chars", table_cell_style), Paragraph("1.3792 ms", table_cell_style), Paragraph("1.4353 ms", table_cell_style), Paragraph("0.5583 ms", table_cell_style), Paragraph("0.5682 ms", table_cell_style), Paragraph("2.50x", table_cell_style)],
        [Paragraph("10,000 chars", table_cell_style), Paragraph("2.8358 ms", table_cell_style), Paragraph("2.9351 ms", table_cell_style), Paragraph("1.1191 ms", table_cell_style), Paragraph("1.1346 ms", table_cell_style), Paragraph("2.55x", table_cell_style)],
    ]
    bench_table = Table(bench_data, colWidths=[90, 85, 85, 80, 80, 84])
    bench_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(bench_table)
    story.append(Spacer(1, 10))

    # Section 6
    story.append(Paragraph("6. Suggestions for Improving the Cipher's Security", h1_style))
    story.append(Paragraph(
        "1. <b>Autokey Key Scheduling:</b> Replace the periodic repeating Vigenère keyword with an Autokey stream (where subsequent key characters are drawn from plaintext: <code>K[i] = P[i - L_V]</code>). This eliminates the periodic alignment exploited by the attack while preserving strict O(N) linear runtime.",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Higher-Dimensional Matrix (3x3 or 4x4):</b> Expanding block size to m=3 or m=4 scales the invertible matrix key space to 1.6 &times; 10<sup>12</sup> and 8.6 &times; 10<sup>21</sup>, rendering exhaustive matrix evaluation completely intractable with negligible linear overhead.",
        bullet_style
    ))
    story.append(Paragraph(
        "3. <b>Non-Linear S-Box Permutation:</b> Interposing a non-linear substitution stage between Vigenère and Hill disrupts linear modular congruences over &Zopf;<sub>26</sub>.",
        bullet_style
    ))
    story.append(Spacer(1, 8))

    # Section 7
    story.append(Paragraph("7. Code Submission & Execution Details", h1_style))
    story.append(Paragraph(
        "All project source files are hosted in the public GitHub repository:<br/>"
        "<b>Repository Link:</b> <font color='#2B6CB0'><u>https://github.com/ameemakhtr/NIS_CCP</u></font>",
        body_style
    ))
    story.append(Paragraph(
        "<b>Repository Contents:</b><br/>"
        "&bull; <code>custom_cipher.py</code>: Hybrid cipher implementation & baseline Shift cipher.<br/>"
        "&bull; <code>attack.py</code>: Frequency analyzer & Known-Plaintext Attack solver.<br/>"
        "&bull; <code>benchmark.py</code>: Latency & throughput benchmarking suite.<br/>"
        "&bull; <code>test_suite.py</code>: Automated unit tests.<br/>"
        "&bull; <code>live_test.py</code>: Standalone live demonstration script.<br/>"
        "&bull; <code>main.py</code>: Interactive CLI application.",
        body_style
    ))
    story.append(Paragraph("<b>Execution Command:</b> <code>python main.py --demo</code>", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated PDF report: {filename}")


if __name__ == "__main__":
    build_pdf("REPORT.pdf")
