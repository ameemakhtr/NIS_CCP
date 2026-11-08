import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, Preformatted, CondPageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import pypdf
from custom_cipher import CustomHybridCipher, add_padding

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:  # Skip cover page
            self.saveState()
            self.setFont("Times-Roman", 9.5)
            self.setFillColor(colors.HexColor("#555555"))
            
            # Header
            self.drawString(54, 746, "Complex Computing Problem Report | CT-486: Network and Information Security")
            self.setStrokeColor(colors.HexColor("#D0D5DD"))
            self.setLineWidth(0.6)
            self.line(54, 738, 558, 738)
            
            # Footer
            self.line(54, 46, 558, 46)
            self.drawRightString(558, 34, f"Page {self._pageNumber} of {page_count}")
            self.drawString(54, 34, "Department of Computer Science & IT, NED University")
            self.restoreState()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def build_pdf():
    pdf_filename = os.path.join(SCRIPT_DIR, "Complex_Computing_Problem_Report.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=24,
        leading=28,
        alignment=1,  # Center
        textColor=colors.HexColor("#1A252F")
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=15,
        leading=19,
        alignment=1,
        textColor=colors.HexColor("#2C3E50")
    )

    dept_style = ParagraphStyle(
        'CoverDept',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12.5,
        leading=16.5,
        alignment=1,
        textColor=colors.HexColor("#333333")
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        spaceBefore=0,
        spaceAfter=7,
        textColor=colors.HexColor("#1A252F")
    )

    sub_heading = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=10.5,
        leading=14,
        spaceBefore=5,
        spaceAfter=3,
        textColor=colors.HexColor("#2C3E50")
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        spaceAfter=5,
        alignment=4,  # Justify
        textColor=colors.HexColor("#222222")
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.0,
        leading=12.5,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3,
        alignment=4,
        textColor=colors.HexColor("#222222")
    )

    numbered_style = ParagraphStyle(
        'NumberedStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.0,
        leading=12.5,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3,
        alignment=4,
        textColor=colors.HexColor("#222222")
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.0,
        leading=10.2,
        textColor=colors.HexColor("#1A252F")
    )

    story = []

    # =========================================================
    # PAGE 1: COVER PAGE
    # =========================================================
    story.append(Spacer(1, 28))
    story.append(Paragraph("Complex Computing Problem Report", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("CT-486: Network and Information Security", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Final Year - Cyber Security", dept_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Batch: 2023", dept_style))
    story.append(Spacer(1, 24))

    # NED Logo
    logo_path = os.path.join(SCRIPT_DIR, "ned_logo_1.png")
    if os.path.exists(logo_path):
        story.append(RLImage(logo_path, width=2.0*inch, height=2.0*inch))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Group Members:", subtitle_style))
    story.append(Spacer(1, 10))

    members_data = [
        [Paragraph("<b>Mr. Ameem Akhtar</b> .........................................................", body_style), Paragraph("<b>(CR-23013)</b>", body_style)],
        [Paragraph("<b>Mr. Minhal Rizvi</b> .........................................................", body_style), Paragraph("<b>(CR-23017)</b>", body_style)],
        [Paragraph("<b>Mr. Muhammad Usman</b> .....................................................", body_style), Paragraph("<b>(CR-23038)</b>", body_style)],
        [Paragraph("<b>Mr. Maaz Wasim</b> .........................................................", body_style), Paragraph("<b>(CR-23041)</b>", body_style)],
    ]
    t_members = Table(members_data, colWidths=[3.8*inch, 1.8*inch])
    t_members.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_members)

    story.append(Spacer(1, 34))
    story.append(Paragraph("<b>Submitted to:</b> Prof. Dr. Shariq Mahmood Khan (Professor, Department of CS & IT)", body_style))
    story.append(Paragraph("<b>Submission Date:</b> November 08, 2026", body_style))
    story.append(PageBreak())

    # Every measured figure below comes from results.json, written by benchmark.py
    with open(os.path.join(SCRIPT_DIR, "results.json"), encoding="utf-8") as handle:
        results = json.load(handle)
    cipher_rows = results["ciphers"]
    by_length = results["attack"]["by_length"]
    by_known = results["attack"]["by_known"]
    freq = results["frequency"]
    stats = freq["ciphers"]
    trials = by_length[0]["trials"]
    at_1000 = next(row for row in cipher_rows if row["length"] == 1000)
    full_recovery = [row for row in by_length if row["success_rate"] == 100.0]
    typical_ms = sum(row["avg_time_ms"] for row in full_recovery) / len(full_recovery)
    worst_ms = max(row["max_time_ms"] for row in full_recovery)
    overheads = [row["custom_enc_ms"] / row["shift_enc_ms"] for row in cipher_rows]

    def add_table(data, widths):
        table = Table(data, colWidths=[w * inch for w in widths])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.0),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")])
        ]))
        story.append(KeepTogether([table, Spacer(1, 5)]))

    def add_code(text):
        table = Table([[Preformatted(text, code_style)]], colWidths=[6.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D1D8E0")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 4))

    def add_text(text, style=body_style):
        story.append(Paragraph(text, style))

    # =========================================================
    # SECTION 1: PROBLEM AND DESIGN OVERVIEW
    # =========================================================
    story.append(Spacer(1, 8))
    story.append(Paragraph("1. Problem Statement and Design Overview", section_heading))
    add_text("The brief asks for a custom cipher built from at least two classical ciphers, in at least two stages that each use a different technique, with a key of at least 10 characters; a program that encrypts and decrypts A-Z text of different lengths; an attack that breaks the cipher; and an analysis of its efficiency against a single-stage Shift cipher.")
    add_text("This project combines a <b>Vigenere cipher</b> (polyalphabetic substitution) with a <b>2 &times; 2 Hill cipher</b> (polygraphic matrix transformation over Z<sub>26</sub>). It is implemented in Python (<font face='Courier'>custom_cipher.py</font>), and the attack is a <b>known-plaintext attack</b> (<font face='Courier'>attack.py</font>). The main result is that the second stage hides letter frequencies well but adds little real security: both stages are linear, and the combination is broken in about a second by an attacker who knows roughly 40 letters of a message.")

    story.append(Paragraph("<b>Mathematical Definition</b>", sub_heading))
    add_text("Letters map to A=0, ..., Z=25. The padded plaintext P is encrypted with a Vigenere key K<sub>vig</sub> of length L &ge; 10 and an invertible matrix K<sub>hill</sub> = [[a, b], [c, d]]:")
    add_code(
        "Stage 1 (Vigenere):  C1[i] = (P[i] + Kvig[i mod L]) mod 26\n"
        "Stage 2 (Hill):      [C[2j], C[2j+1]]^T = Khill * [C1[2j], C1[2j+1]]^T mod 26"
    )
    add_text("Stage 2 can be undone only if gcd(det K<sub>hill</sub>, 26) = 1, that is, the determinant Delta = (ad - bc) mod 26 is neither even nor a multiple of 13. Decryption uses K<sub>hill</sub><sup>-1</sup> = Delta<sup>-1</sup> &middot; [[d, -b], [-c, a]] mod 26. There are |GL(2, Z<sub>26</sub>)| = 157,248 such matrices.")

    story.append(Paragraph("<b>How the Classical Techniques Are Combined</b>", sub_heading))
    bullets = [
        "<b>Keys.</b> The cipher takes two keys, each at least 10 letters after removing non-letters; shorter keys are rejected. The Vigenere key is used letter by letter. The Hill phrase is reduced to a matrix by adding each of its letters, in turn, into entry a, b, c or d mod 26, so every letter of the phrase affects the matrix. If the determinant is not invertible, entry d is incremented (carrying into c, b, a) until it is.",
        "<b>Order of the stages.</b> Vigenere runs first because it needs to act on individual letters at known positions. Its output is cut into pairs and each pair is multiplied by the Hill matrix, so each ciphertext letter depends on two Vigenere-shifted letters and on the key letters at both positions.",
        "<b>What each stage contributes.</b> Vigenere replaces one fixed alphabet with L alphabets, which flattens the letter histogram. Hill then mixes neighbouring letters, which hides the repeating key alphabet from column-by-column Vigenere analysis, since a ciphertext letter no longer belongs to a single Caesar alphabet.",
        "<b>Padding.</b> Hill needs an even number of letters. An odd-length message gets 'X' and an even-length message gets 'XA'. Padding is always added so that decryption can remove it without guessing: a final 'X' means one padding letter, anything else means two. A message genuinely ending in X, such as FOXX, therefore decrypts exactly.",
    ]
    for bullet in bullets:
        add_text("&bull; " + bullet, bullet_style)

    example = CustomHybridCipher("CRYPTOGRAPHYKEY", "HILLCIPHERKEY")
    padded = add_padding("ATTACKATDAWN")
    stage1 = "".join(chr(n + 65) for n in example._vigenere_encrypt(padded))
    story.append(Paragraph("<b>Worked Example</b>", sub_heading))
    add_code(
        f"Keys:        Kvig = CRYPTOGRAPHYKEY (L = 15), Hill phrase = HILLCIPHERKEY\n"
        f"Matrix:      Khill = {[list(example.hill_mat[:2]), list(example.hill_mat[2:])]}\n"
        f"Plaintext:   ATTACKATDAWN\n"
        f"Padded:      {padded}\n"
        f"Stage 1:     {stage1}\n"
        f"Stage 2:     {example.encrypt('ATTACKATDAWN')}   (final ciphertext)\n"
        f"Decrypted:   {example.decrypt(example.encrypt('ATTACKATDAWN'))}"
    )
    story.append(PageBreak())

    # =========================================================
    # SECTION 2: ALGORITHMS
    # =========================================================
    story.append(Spacer(1, 8))
    story.append(Paragraph("2. Encryption and Decryption Algorithms", section_heading))
    story.append(Paragraph("<b>Algorithm 1: Encryption</b>", sub_heading))
    add_code(
        "Input:  Plaintext P, Vigenere key Kvig (|Kvig| >= 10), Hill phrase H (|H| >= 10)\n"
        "Output: Ciphertext C\n"
        " 1: P <- keep only letters A-Z of UpperCase(P)\n"
        " 2: if P is empty then return empty string\n"
        " 3: if |P| is odd then P <- P + 'X' else P <- P + 'XA'\n"
        " 4: Khill <- DeriveMatrix(H)\n"
        " 5: for i = 0 to |P| - 1 do\n"
        " 6:     C1[i] <- (P[i] + Kvig[i mod |Kvig|]) mod 26\n"
        " 7: for j = 0 to |P|/2 - 1 do\n"
        " 8:     C[2j]   <- (a * C1[2j] + b * C1[2j+1]) mod 26\n"
        " 9:     C[2j+1] <- (c * C1[2j] + d * C1[2j+1]) mod 26\n"
        "10: return C"
    )
    story.append(Paragraph("<b>Algorithm 2: Decryption</b>", sub_heading))
    add_code(
        "Input:  Ciphertext C, Vigenere key Kvig, Hill phrase H\n"
        "Output: Original plaintext P\n"
        " 1: if |C| is odd then reject as invalid\n"
        " 2: Khill <- DeriveMatrix(H)\n"
        " 3: Kinv <- ModInverse(det Khill, 26) * [[d, -b], [-c, a]] mod 26\n"
        " 4: for j = 0 to |C|/2 - 1 do\n"
        " 5:     C1[2j]   <- (Kinv.a * C[2j] + Kinv.b * C[2j+1]) mod 26\n"
        " 6:     C1[2j+1] <- (Kinv.c * C[2j] + Kinv.d * C[2j+1]) mod 26\n"
        " 7: for i = 0 to |C| - 1 do\n"
        " 8:     P[i] <- (C1[i] - Kvig[i mod |Kvig|]) mod 26\n"
        " 9: if P ends in 'X' then remove 1 letter else remove 2 letters\n"
        "10: return P"
    )
    story.append(Paragraph("<b>DeriveMatrix(H)</b>", sub_heading))
    add_code(
        "1: [a, b, c, d] <- [0, 0, 0, 0]\n"
        "2: for i = 0 to |H| - 1 do  entry[i mod 4] <- (entry[i mod 4] + H[i]) mod 26\n"
        "3: while gcd(ad - bc, 26) != 1 do  increment d, carrying into c, b, a at 26\n"
        "4: return [[a, b], [c, d]]"
    )
    add_text(f"The unit tests in <font face='Courier'>test_suite.py</font> check exact round trips for every length from 1 to 26, a 380-letter message, and padding-like endings such as X, XX, XA and FOXX.")

    # =========================================================
    # SECTION 3: SECURITY ANALYSIS
    # =========================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Security Analysis", section_heading))
    add_text("<b>Key space.</b> With L = 10 there are 26<super>10</super> &times; 157,248 &asymp; 2.2 &times; 10<super>19</super> key pairs, against 26 for the Shift cipher, so exhaustive search of both keys together is impractical. This number overstates the security, because the attack in Section 4 never searches the Vigenere key: it searches the matrices alone and solves for the Vigenere key directly.")
    add_text("<b>Structure.</b> Substituting Stage 1 into Stage 2 gives C<sub>j</sub> = K<sub>hill</sub> &middot; P<sub>j</sub> + K<sub>hill</sub> &middot; V<sub>j</sub> mod 26, where V<sub>j</sub> is the pair of key letters at block j. The whole cipher is therefore a single affine Hill cipher whose constant term repeats with the key. Composing two linear stages does not create a stronger kind of function, and that is the weakness the attack exploits.")
    add_text(f"<b>Confusion and diffusion.</b> Vigenere provides confusion: the same letter encrypts differently at different positions. Diffusion is limited to one pair. Changing one plaintext letter changed <b>{freq['avg_ciphertext_letters_changed']}</b> ciphertext letters on average and never more than {freq['max_ciphertext_letters_changed']}, whereas a modern block cipher changes about half of its output.")
    add_text(f"<b>Frequency analysis.</b> Letter counts of each ciphertext were compared with the expected English distribution, using the Index of Coincidence IoC = &sum; f<sub>i</sub>(f<sub>i</sub> - 1) / [N(N - 1)] and the chi-squared distance from English. Figures are averages over {freq['samples']} random key sets and {freq['length']:,}-letter passages of English technical documentation, which runs slightly above the textbook English IoC of 0.0667.")
    rows = [["Text", "Mean IoC", "Std. dev.", "Chi-squared vs English"]]
    for name in ["Plaintext", "Shift", "Hill only", "Vigenere only", "Custom"]:
        label = {"Custom": "Custom (Vigenere + Hill)", "Shift": "Shift ciphertext"}.get(name, name)
        rows.append([label, f"{stats[name]['ioc']:.4f}", f"{stats[name]['ioc_stdev']:.4f}", f"{stats[name]['chi_squared']:,.1f}"])
    add_table(rows, [2.3, 1.2, 1.2, 1.8])
    plot1_path = os.path.join(SCRIPT_DIR, "frequency_ioc_analysis.png")
    story.append(RLImage(plot1_path, width=6.5*inch, height=2.65*inch))
    add_text("<font size=7.5><i>Figure 1: Measured letter frequency of each ciphertext against expected English, and measured IoC.</i></font>")
    add_text(f"The Shift cipher has exactly the plaintext's IoC ({stats['Shift']['ioc']:.4f}) because it only renames letters. The custom cipher reaches {stats['Custom']['ioc']:.4f}, close to the uniform value of 0.0385, and its histogram no longer resembles English. The chi-squared value shows only that the ciphertext is far from English. Frequency analysis on its own therefore does not recover the key here, so it serves as a measure of how well the statistics are hidden; the cipher is broken by the attack below.")

    # =========================================================
    # SECTION 4: ATTACK
    # =========================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("4. Attack Method and Results", section_heading))
    add_text("<b>Scenario.</b> The attacker has the whole ciphertext and the plaintext of its first M letters, such as a predictable message header, and knows the algorithm and that keys have at least 10 letters. The attacker does <b>not</b> know either key or the Vigenere key length.")
    story.append(Paragraph("<b>Algorithm 3: Known-Plaintext Attack</b>", sub_heading))
    add_code(
        "Input:  Ciphertext C, known plaintext P[0..M-1]\n"
        "Output: Khill, Kvig and the full plaintext, or failure\n"
        " 1: Pool <- all 157,248 invertible 2x2 matrices mod 26 with their inverses\n"
        " 2: for L = 10 to M - 20 do                       // candidate key lengths\n"
        " 3:     for each matrix K in Pool do\n"
        " 4:         for each known pair j do\n"
        " 5:             [x1, x2]^T <- Kinv * [C[2j], C[2j+1]]^T mod 26\n"
        " 6:             k <- (x - P) mod 26 for both letters\n"
        " 7:             if k disagrees with a key letter already set at i mod L then reject K\n"
        " 8:         if K was not rejected then decrypt all of C with (K, k); return\n"
        " 9: return failure"
    )
    add_text("<b>Why it works.</b> Once the correct matrix is guessed, Stage 2 is undone and Stage 1 reduces to k[i] = x[i] - P[i], which directly reveals the Vigenere key. A wrong matrix produces a stream that does not repeat every L letters. The check exploits exactly the two properties identified in Section 3: linearity and the repeating key. Known pairs are tested grouped by key position, so a wrong matrix is usually rejected after a few checks.")
    add_text("<b>How much known text is needed.</b> At least L letters are needed to see every key letter, and extra letters are needed to reject wrong matrices. Because 26 = 2 &times; 13, a matrix that is correct mod 13 and wrong only mod 2 passes each check about half the time. In a separate experiment (<font face='Courier'>false_match_experiment.py</font>) with L = 20, 8 extra letters returned a wrong key in 14 of 150 runs and 20 extra letters in 0 of 150, so the attack requires M &ge; L + 20 and reports failure otherwise.")
    add_text(f"<b>Results.</b> Each row is {trials} trials, each with new random keys (Vigenere key of 10 to 20 letters) and a new random English passage. A trial counts as a success only if the complete message is recovered exactly. Time excludes the one-off construction of the matrix pool, which took {results['gl2_precompute_ms']:.0f} ms.")
    story.append(Paragraph("<b>Table 1: Success and effort by ciphertext length (first 25% of the message known)</b>", sub_heading))
    rows = [["Ciphertext length", "Known letters", "Success rate", "Average time (ms)", "Worst time (ms)", "Average matrices tried"]]
    for row in by_length:
        rows.append([f"{row['length']:,}", f"{row['known_chars']:,}", f"{row['success_rate']:.1f}%", f"{row['avg_time_ms']:.1f}", f"{row['max_time_ms']:.1f}", f"{row['avg_matrices']:,}"])
    add_table(rows, [1.2, 0.95, 0.95, 1.15, 1.05, 1.2])
    story.append(Paragraph("<b>Table 2: Success and effort by amount of known plaintext (1,000-letter ciphertext)</b>", sub_heading))
    rows = [["Known letters", "Success rate", "Average time (ms)", "Worst time (ms)", "Average matrices tried"]]
    for row in by_known:
        rows.append([f"{row['known_chars']}", f"{row['success_rate']:.1f}%", f"{row['avg_time_ms']:.1f}", f"{row['max_time_ms']:.1f}", f"{row['avg_matrices']:,}"])
    add_table(rows, [1.2, 1.2, 1.4, 1.3, 1.4])
    add_text(f"Success is decided by the amount of known text, not by the ciphertext length as such. Short messages fail in Table 1 only because 25% of them is too few letters. With 40 or more known letters, enough for the longest key tested, recovery was exact in every trial. When recovery succeeded, the attack averaged about {typical_ms:.0f} ms and at most {worst_ms:.0f} ms, and its cost did not grow with the ciphertext length.")

    # =========================================================
    # SECTION 5: PERFORMANCE
    # =========================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("5. Performance and Efficiency", section_heading))
    add_text("<b>Time complexity</b>, for a message of N letters:")
    for bullet in [
        "<b>Encryption:</b> Vigenere does N additions and Hill does N/2 matrix multiplications of constant size, so the total is <b>O(N)</b>.",
        "<b>Decryption:</b> inverting a 2 &times; 2 matrix takes constant time, followed by the same two passes in reverse, so the total is <b>O(N)</b>.",
        "<b>Shift cipher:</b> one addition per letter, also <b>O(N)</b>. All three use O(N) space. The custom cipher is slower by a constant factor only.",
        f"<b>Attack:</b> the matrix pool is a one-off 26<super>4</super> = 456,976 determinant checks. The search is O(T &middot; |GL| &middot; c), where T is the number of key lengths tried, |GL| = 157,248 and c is the average number of checks before rejection, which is small and in the worst case M. Recovering the message afterwards is O(N).",
    ]:
        add_text("&bull; " + bullet, bullet_style)
    story.append(Spacer(1, 3))
    environment = results["environment"]
    story.append(CondPageBreak(1.9*inch))
    story.append(Paragraph(f"<b>Table 3: Measured cipher time in ms (average of 50 runs, Python {environment['python']})</b>", sub_heading))
    rows = [["Length", "Custom encrypt", "Custom decrypt", "Shift encrypt", "Shift decrypt", "Encrypt overhead", "Custom letters/s"]]
    for row in cipher_rows:
        rows.append([f"{row['length']:,}", f"{row['custom_enc_ms']:.4f}", f"{row['custom_dec_ms']:.4f}", f"{row['shift_enc_ms']:.4f}", f"{row['shift_dec_ms']:.4f}", f"{row['custom_enc_ms'] / row['shift_enc_ms']:.2f}x", f"{row['length'] / row['custom_enc_ms'] * 1000:,.0f}"])
    add_table(rows, [0.7, 1.0, 1.0, 0.9, 0.9, 1.0, 1.0])
    plot2_path = os.path.join(SCRIPT_DIR, "benchmark_comparison.png")
    story.append(RLImage(plot2_path, width=6.5*inch, height=2.65*inch))
    add_text("<font size=7.5><i>Figure 2: Measured cipher time against message length, and attack success against known plaintext.</i></font>")
    add_text(f"Time grows linearly with length for both ciphers, as the analysis predicts. Encrypting 1,000 letters took {at_1000['custom_enc_ms']:.3f} ms with the custom cipher and {at_1000['shift_enc_ms']:.3f} ms with the Shift cipher. The two-stage design costs {min(overheads):.1f}x to {max(overheads):.1f}x the time of the single-stage cipher, and in return it hides letter frequencies that the Shift cipher exposes completely. These are timings of interpreted Python on one machine, so the ratios are more meaningful than the absolute values.")

    # =========================================================
    # SECTION 6: IMPROVEMENTS AND SUBMISSION
    # =========================================================
    story.append(Spacer(1, 4))
    story.append(Paragraph("6. Improving Security Without Significantly Increasing Complexity", section_heading))
    add_text("The attack depends on linearity and on the repeating key, so useful changes must remove one of these. Each option below stays O(N). They would raise the attacker's cost but were not implemented or measured here, and none would make the cipher secure by modern standards.")
    for bullet in [
        "<b>1. Keyed non-linear substitution between the stages.</b> Pass each Vigenere output letter through a secret permutation of the alphabet, one table lookup per letter. The relation k[i] = x[i] - P[i] then no longer holds, so the key letters cannot be read off after guessing the matrix.",
        "<b>2. Keyed columnar transposition between the stages.</b> Reordering letters by a secret permutation separates known plaintext from the ciphertext positions it produces, so the attacker must also search the permutation.",
        "<b>3. A non-repeating keystream.</b> Derive a different Vigenere key for each message from the main key and a per-message value. The periodicity check that rejects wrong matrices then has nothing to test.",
    ]:
        add_text(bullet, bullet_style)
    add_text("Two changes that seem helpful are weak on their own. A longer Vigenere key only raises the known text needed (M &ge; L + 20). A larger Hill matrix leaves the system linear: subtracting blocks a whole number of key periods apart cancels the Vigenere term and gives Delta C = K<sub>hill</sub> &middot; Delta P, which can be solved with linear algebra rather than search.")
    story.append(Paragraph("7. Code Submission", section_heading))
    add_text("The source code, tests and measurement scripts are at: <b><u>https://github.com/ameemakhtr/NIS_CCP</u></b>. Running <font face='Courier'>python benchmark.py</font> reproduces <font face='Courier'>results.json</font>, from which every table and figure above is generated.")

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {pdf_filename}")

if __name__ == '__main__':
    build_pdf()
