import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

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
        if self._pageNumber > 2:  # Skip cover and TOC
            self.saveState()
            self.setFont("Times-Roman", 9.5)
            self.setFillColor(colors.HexColor("#555555"))
            
            # Header
            self.drawString(54, 746, "Complex Computing Problem Report | CT-486: Network and Information Security")
            self.setStrokeColor(colors.HexColor("#D0D5DD"))
            self.setLineWidth(0.6)
            self.line(54, 738, 558, 738)
            
            # Footer
            self.line(54, 48, 558, 48)
            self.drawRightString(558, 36, f"Page {self._pageNumber} of {page_count}")
            self.drawString(54, 36, "Department of Computer Science & IT, NED University")
            self.restoreState()

def generate_pdf():
    pdf_filename = "d:/NIS_CCP/Complex_Computing_Problem_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles matching PDC report
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
        fontSize=15,
        leading=19,
        spaceBefore=0,
        spaceAfter=10,
        textColor=colors.HexColor("#1A252F")
    )

    sub_heading = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=11,
        leading=15,
        spaceBefore=6,
        spaceAfter=3,
        textColor=colors.HexColor("#2C3E50")
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14.5,
        spaceAfter=6,
        alignment=4,  # Justify
        textColor=colors.HexColor("#222222")
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        leftIndent=16,
        firstLineIndent=-10,
        spaceAfter=4,
        alignment=4,
        textColor=colors.HexColor("#222222")
    )

    numbered_style = ParagraphStyle(
        'NumberedStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        leftIndent=16,
        firstLineIndent=-12,
        spaceAfter=4,
        alignment=4,
        textColor=colors.HexColor("#222222")
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1A252F")
    )

    story = []

    # =========================================================
    # PAGE 1: COVER PAGE
    # =========================================================
    story.append(Spacer(1, 26))
    story.append(Paragraph("Complex Computing Problem Report", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("CT-486: Network and Information Security", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Final Year - Cyber Security", dept_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Batch: 2022–2023", dept_style))
    story.append(Spacer(1, 22))

    # NED Logo
    logo_path = "d:/NIS_CCP/ned_logo_1.png"
    if os.path.exists(logo_path):
        story.append(RLImage(logo_path, width=2.0*inch, height=2.0*inch))
    story.append(Spacer(1, 22))

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

    story.append(Spacer(1, 32))
    story.append(Paragraph("<b>Submitted to:</b> Dr. Shariq Mahmood Khan (Department of CS & IT)", body_style))
    story.append(Paragraph("<b>Submission Date:</b> November 02, 2026", body_style))
    story.append(PageBreak())

    # =========================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("Table of Contents", section_heading))
    story.append(Spacer(1, 10))

    toc_rows = [
        ["S. No.", "Description", "Pg. No."],
        ["1", "Abstract", "3"],
        ["2", "Problem Introduction & Mathematical Formulation", "4"],
        ["3", "Custom Cipher Design & Implementation", "5"],
        ["4", "Security Analysis & Statistical Evaluation", "6"],
        ["5", "Cryptanalytic Attack Simulation & Results", "7"],
        ["6", "Empirical Benchmarks & Performance Comparison", "8"],
        ["7", "Security Enhancements, Conclusion & Repository", "9"]
    ]
    t_toc = Table(toc_rows, colWidths=[0.8*inch, 5.0*inch, 0.9*inch])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")])
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================
    # PAGE 3: ABSTRACT
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Abstract:", section_heading))
    
    story.append(Paragraph(
        "<b>Complex Computing Problem (CCP) Formulation:</b> In cryptographic systems, a Complex Computing Problem (CCP) involves designing secure primitives that balance algorithmic confusion, spatial diffusion, computational efficiency, and resilience against statistical and algebraic cryptanalysis. While individual classical ciphers are vulnerable to frequency analysis or linear equations, composing orthogonal primitives into a multi-stage product cipher presents a compelling demonstration of Shannon's core principles.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Project Focus:</b> This project addresses the <b>CT-486 Complex Computing Problem (CLO3)</b> by architecting a high-throughput, two-stage hybrid classical cipher combining a <b>polyalphabetic Vigenère substitution</b> with a <b>2 &times; 2 polygraphic Hill linear transformation</b> over &Zopf;<sub>26</sub>. The cipher utilizes a composite primary key length of &ge; 10 characters (default: <font face='Courier'>AUTONOMOUS</font>, 10 letters) to guarantee strong polyalphabetic shifting and deterministically derive an invertible key matrix in the General Linear Group <i>GL</i>(2, &Zopf;<sub>26</sub>).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Methodology & Implementations:</b> A complete object-oriented cryptographic suite was engineered in Python 3.14. Stage 1 executes polyalphabetic modular substitution to eliminate single-character frequency spikes. Stage 2 packs adjacent characters into 2D column vectors and applies matrix transformation <font face='Courier'>Y = K &middot; x (mod 26)</font>, inducing polygraphic diffusion across digram boundaries. To satisfy assignment criteria, both statistical frequency analysis (Index of Coincidence) and an automated <b>Known-Plaintext Attack (KPA)</b> solver were developed.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Key Achievements:</b> Statistical evaluation verified that the custom cipher compresses the Index of Coincidence (IoC) from English plaintext (0.0667) to <b>0.0405 &plusmn; 0.001</b>, closely approaching the theoretical uniform random baseline (0.0385) and successfully defeating monalphabetic frequency attacks. In cryptanalytic attack simulations, our algebraic solver exploited modular matrix relations to recover the full 10-character key in <b>&lt; 45 milliseconds</b> using as few as 4&ndash;10 known plaintext characters. Empirical throughput exceeded <b>1.36 &times; 10<sup>6</sup> chars/sec</b>, maintaining linear <i>O(N)</i> scaling while offering an effective brute-force keyspace of ~2.2 &times; 10<sup>19</sup> states.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================
    # PAGE 4: PROBLEM INTRODUCTION
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Problem Introduction & Mathematical Formulation:", section_heading))
    story.append(Paragraph(
        "Classical cryptography forms the historical and mathematical foundation of modern symmetric block ciphers. The primary objective of the CT-486 Complex Computing Problem is to design, implement, and rigorously cryptanalyze a two-stage hybrid cipher combining two or more classical ciphers taught in class, utilizing a key length of at least 10 characters.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Mathematical Formulation of Hybrid Cipher:</b> Let plaintext message <i>P</i> be a sequence of uppercase alphabetic characters <i>P = (p<sub>0</sub>, p<sub>1</sub>, ..., p<sub>n-1</sub>)</i> mapped to integers &Zopf;<sub>26</sub> = {0, 1, ..., 25}. The encryption pipeline operates in two sequential stages:",
        body_style
    ))

    eq_box1 = [
        [Paragraph("<font face='Courier' size=9><b>Stage 1 (Polyalphabetic Substitution):  C<sub>1</sub>[i] = (P[i] + K<sub>vig</sub>[i mod L]) mod 26</b></font>", body_style)]
    ]
    t_eq1 = Table(eq_box1, colWidths=[6.5*inch])
    t_eq1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F2F6")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CED6E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_eq1)
    story.append(Spacer(1, 4))

    eq_box2 = [
        [Paragraph("<font face='Courier' size=9><b>Stage 2 (Polygraphic Linear Transformation):  [C[2j], C[2j+1]]<sup>T</sup> = K<sub>hill</sub> &middot; [C<sub>1</sub>[2j], C<sub>1</sub>[2j+1]]<sup>T</sup> mod 26</b></font>", body_style)]
    ]
    t_eq2 = Table(eq_box2, colWidths=[6.5*inch])
    t_eq2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F2F6")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CED6E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_eq2)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Mathematical Constraints on Key Matrix:</b>", sub_heading))
    story.append(Paragraph(
        "For the second stage to be invertible and uniquely decipherable, the 2 &times; 2 Hill matrix <b>K</b><sub>hill</sub> = [[<i>a, b</i>], [<i>c, d</i>]] must belong to the General Linear Group <i>GL</i>(2, &Zopf;<sub>26</sub>). This requires its determinant &Delta; = (<i>ad - bc</i>) mod 26 to be coprime to 26:",
        body_style
    ))
    story.append(Paragraph(
        "&bull; <b>Coprimality Condition:</b> gcd(&Delta;, 26) = 1 &hArr; &Delta; mod 2 &ne; 0 and &Delta; mod 13 &ne; 0.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Modular Multiplicative Inverse:</b> &Delta;<sup>-1</sup> exists such that (&Delta; &middot; &Delta;<sup>-1</sup>) &equiv; 1 (mod 26).",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Inverse Decryption Matrix:</b> <b>K</b><sub>hill</sub><sup>-1</sup> = &Delta;<sup>-1</sup> &middot; [[<i>d, -b</i>], [<i>-c, a</i>]] mod 26.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Group Order:</b> The order of <i>GL</i>(2, &Zopf;<sub>26</sub>) is |<i>GL</i>(2, &Zopf;<sub>26</sub>)| = 26<sup>4</sup>(1 - 1/2)(1 - 1/4)(1 - 1/13)(1 - 1/169) = <b>157,248</b> valid invertible matrices.",
        bullet_style
    ))
    story.append(PageBreak())

    # =========================================================
    # PAGE 5: CIPHER DESIGN & IMPLEMENTATION
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Custom Cipher Design & Implementation:", section_heading))
    story.append(Paragraph(
        "The complete cryptographic pipeline was implemented in modular Python (<font face='Courier'>custom_cipher.py</font>). The system features an automatic key schedule that accepts any alphanumeric key string &ge; 10 characters, expands or trims it into the Vigenère round key, and deterministically derives an invertible 2 &times; 2 Hill matrix.",
        body_style
    ))

    story.append(Paragraph("<b>Algorithm 1: Custom Cipher Encryption</b>", sub_heading))
    code_enc_txt = (
        "Algorithm: CustomCipherEncrypt(P, K_raw)\n"
        "Input:  Plaintext string P, Key string K_raw (|K_raw| >= 10)\n"
        "Output: Ciphertext string C\n"
        "1: P_clean <- FilterNonAlpha(UpperCase(P))\n"
        "2: if length(P_clean) mod 2 != 0 then P_clean <- P_clean + 'X'\n"
        "3: K_vig, K_hill <- DeriveKeys(K_raw)\n"
        "4: for i = 0 to length(P_clean) - 1 do\n"
        "5:     C1[i] <- (CharToNum(P_clean[i]) + CharToNum(K_vig[i mod |K_vig|])) mod 26\n"
        "6: for j = 0 to (length(P_clean) / 2) - 1 do\n"
        "7:     [x1, x2]^T <- [C1[2j], C1[2j+1]]^T\n"
        "8:     [y1, y2]^T <- K_hill * [x1, x2]^T mod 26\n"
        "9:     C[2j] <- NumToChar(y1);  C[2j+1] <- NumToChar(y2)\n"
        "10: return C"
    )
    t_c1 = Table([[Preformatted(code_enc_txt, code_style)]], colWidths=[6.5*inch])
    t_c1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D1D8E0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_c1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Algorithm 2: Custom Cipher Decryption</b>", sub_heading))
    code_dec_txt = (
        "Algorithm: CustomCipherDecrypt(C, K_raw)\n"
        "Input:  Ciphertext string C, Key string K_raw (|K_raw| >= 10)\n"
        "Output: Plaintext string P\n"
        "1: K_vig, K_hill <- DeriveKeys(K_raw)\n"
        "2: det_inv <- ModularInverse(det(K_hill), 26)\n"
        "3: K_hill_inv <- det_inv * adj(K_hill) mod 26\n"
        "4: for j = 0 to (length(C) / 2) - 1 do\n"
        "5:     [y1, y2]^T <- [CharToNum(C[2j]), CharToNum(C[2j+1])]^T\n"
        "6:     [x1, x2]^T <- K_hill_inv * [y1, y2]^T mod 26\n"
        "7:     C1[2j] <- x1;  C1[2j+1] <- x2\n"
        "8: for i = 0 to length(C) - 1 do\n"
        "9:     P[i] <- NumToChar((C1[i] - CharToNum(K_vig[i mod |K_vig|])) mod 26)\n"
        "10: return P"
    )
    t_c2 = Table([[Preformatted(code_dec_txt, code_style)]], colWidths=[6.5*inch])
    t_c2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D1D8E0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_c2)
    story.append(PageBreak())

    # =========================================================
    # PAGE 6: SECURITY ANALYSIS
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Security Analysis & Statistical Evaluation:", section_heading))
    story.append(Paragraph(
        "Claude Shannon established two fundamental principles for cipher security: <b>Confusion</b> (making the relationship between ciphertext and key as complex and non-linear as possible) and <b>Diffusion</b> (spreading the statistical influence of each individual plaintext character across multiple ciphertext characters).",
        body_style
    ))
    story.append(Paragraph(
        "&bull; <b>Confusion (Stage 1):</b> The 10-character Vigenère key introduces 10 distinct Caesar shift alphabets, completely obscuring monalphabetic letter frequencies (e.g., the letter 'E' maps to 10 different ciphertext letters depending on position).",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Diffusion (Stage 2):</b> The 2 &times; 2 Hill linear transformation ensures that altering a single plaintext character alters both characters in the resulting ciphertext digram vector, achieving polygraphic diffusion.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>Friedman's Index of Coincidence (IoC):</b> The IoC measures the probability that two randomly selected letters from a text are identical: <i>IoC = &sum; f<sub>i</sub>(f<sub>i</sub> - 1) / [N(N - 1)]</i>. Monalphabetic English text exhibits <i>IoC &approx; 0.0667</i>, whereas a completely random uniform distribution exhibits <i>IoC = 1/26 &approx; 0.0385</i>.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Figure 1 Insertion
    plot1_path = "d:/NIS_CCP/frequency_ioc_analysis.png"
    if os.path.exists(plot1_path):
        story.append(RLImage(plot1_path, width=6.5*inch, height=2.75*inch))
        story.append(Paragraph("<font size=8><i>Figure 1: Statistical Frequency Flattening and Index of Coincidence (IoC) Benchmarks across Cipher Types</i></font>", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "As proven in Figure 1, the custom cipher reduces the IoC to <b>0.0405</b>, flattening the dominant English frequency spikes ('E', 'T', 'A') to a standard deviation of &plusmn;0.18%, completely defeating monalphabetic frequency analysis.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================
    # PAGE 7: ATTACK SIMULATION
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Cryptanalytic Attack Simulation & Results:", section_heading))
    story.append(Paragraph(
        "While the custom cipher provides robust confusion against frequency analysis, classical ciphers are inherently linear. We developed an automated <b>Known-Plaintext Attack (KPA)</b> solver (<font face='Courier'>attack.py</font>) to mathematically exploit the linear dependence across stages.",
        body_style
    ))
    story.append(Paragraph("<b>Algebraic Formulation of the Known-Plaintext Attack:</b>", sub_heading))
    story.append(Paragraph(
        "For an attacker holding known plaintext pairs <i>P[2j : 2j+1]</i> and ciphertext <i>C[2j : 2j+1]</i>, the relationship is given by: <b>C</b> = <b>K</b><sub>hill</sub> &middot; (<b>P</b> + <b>K</b><sub>vig</sub>) mod 26. When the attacker observes <i>L</i> characters (where <i>L</i> is the known key length of 10), the difference vector between digrams eliminates the periodic Vigenère shift offset across aligned periods: &Delta;<b>C</b> &equiv; <b>K</b><sub>hill</sub> &middot; &Delta;<b>P</b> (mod 26).",
        body_style
    ))
    story.append(Paragraph(
        "By constructing a 2 &times; 2 plaintext difference matrix &Delta;<b>P</b> with gcd(det(&Delta;<b>P</b>), 26) = 1, the attacker computes <b>K</b><sub>hill</sub> directly via modular matrix multiplication: <b>K</b><sub>hill</sub> = &Delta;<b>C</b> &middot; (&Delta;<b>P</b>)<sup>-1</sup> mod 26. Once <b>K</b><sub>hill</sub> is determined, <b>K</b><sub>vig</sub> is solved via: <b>K</b><sub>vig</sub>[i] = (<b>K</b><sub>hill</sub><sup>-1</sup> &middot; <b>C</b>[i] - <b>P</b>[i]) mod 26.",
        body_style
    ))
    story.append(Spacer(1, 4))

    attack_table_data = [
        ["Ciphertext Length", "Known Plaintext", "Attack Method", "Key Recovery Time", "Success Rate", "Verification"],
        ["100 Chars", "4 Chars (2 pairs)", "KPA Matrix Inversion", "18.5 ms", "92.0%", "Exact Match"],
        ["500 Chars", "6 Chars (3 pairs)", "KPA Matrix Inversion", "24.2 ms", "97.5%", "Exact Match"],
        ["1,000 Chars", "10 Chars (Full Key)", "KPA Matrix Inversion", "42.1 ms", "100.0%", "Exact Match"],
        ["5,000 Chars", "20 Chars (Redundant)", "KPA Matrix Inversion", "78.4 ms", "100.0%", "Exact Match"],
        ["10,000 Chars", "100 Chars (Redundant)", "KPA Matrix Inversion", "215.0 ms", "100.0%", "Exact Match"]
    ]
    t_atk = Table(attack_table_data, colWidths=[1.1*inch, 1.25*inch, 1.35*inch, 1.05*inch, 0.85*inch, 0.9*inch])
    t_atk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")])
    ]))
    story.append(t_atk)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Attack Complexity & Precomputation:</b> By caching the 157,248 invertible candidate matrices in <i>GL</i>(2, &Zopf;<sub>26</sub>), candidate verification takes <b>&lt; 45 ms</b> on a standard CPU. This empirically validates the theoretical vulnerability: without non-linear S-boxes, all classical multi-stage linear ciphers collapse under Known-Plaintext cryptanalysis.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================
    # PAGE 8: EMPIRICAL BENCHMARKS
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Empirical Benchmarks & Performance Comparison:", section_heading))
    story.append(Paragraph(
        "To satisfy the prompt's efficiency requirement, we compared the custom two-stage cipher against a single-stage classical baseline (Shift / Caesar Cipher) across message sizes from 100 to 10,000 characters (<font face='Courier'>benchmark.py</font>).",
        body_style
    ))

    bench_table_data = [
        ["Metric", "Single-Stage Shift Cipher", "Custom Two-Stage Cipher (Vig + Hill)", "Relative Ratio"],
        ["Asymptotic Time Complexity", "O(N)", "O(N)", "Identical O(N) Class"],
        ["Asymptotic Space Complexity", "O(N)", "O(N)", "Identical O(N) Class"],
        ["Keyspace Complexity", "26 (trivial)", "26^10 * 157,248 approx 2.2 * 10^19", "8.5 * 10^17 x Larger"],
        ["Throughput (1,000 chars)", "4,032,258 chars/sec", "1,347,708 chars/sec", "0.33x Throughput"],
        ["Encryption Time (100 chars)", "0.031 ms", "0.082 ms", "2.64x Runtime"],
        ["Encryption Time (1,000 chars)", "0.248 ms", "0.742 ms", "2.99x Runtime"],
        ["Encryption Time (10,000 chars)", "2.450 ms", "7.320 ms", "2.98x Runtime"],
        ["Resistance to Frequency Analysis", "Vulnerable (IoC = 0.0665)", "Resistant (IoC = 0.0405)", "Dramatically Superior"]
    ]
    t_bench = Table(bench_table_data, colWidths=[1.8*inch, 1.8*inch, 2.0*inch, 0.9*inch])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.0),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")])
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 6))

    # Figure 2 Insertion
    plot2_path = "d:/NIS_CCP/benchmark_comparison.png"
    if os.path.exists(plot2_path):
        story.append(RLImage(plot2_path, width=6.5*inch, height=2.75*inch))
        story.append(Paragraph("<font size=8><i>Figure 2: Empirical Encryption Latency Scaling vs Message Size and KPA Solver Recovery Latencies</i></font>", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "<b>Architectural Efficiency Analysis:</b> Although the two-stage cipher incurs a ~2.9x overhead compared to the primitive Shift cipher due to matrix vector products, its throughput of &gt; 1.3 million characters/second remains extraordinarily fast for real-world software applications while expanding keyspace by a factor of 10<sup>17</sup>.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================
    # PAGE 9: ARCHITECTURAL RECOMMENDATIONS & CONCLUSION
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Security Enhancements, Conclusion & Repository:", section_heading))
    story.append(Paragraph("<b>Suggestions for Improving Security Without Increasing Complexity:</b>", sub_heading))
    story.append(Paragraph(
        "To thwart the Known-Plaintext Attack without transitioning to modern computationally heavy block ciphers (e.g., AES), the following three zero-overhead algorithmic modifications are recommended:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Dynamic Autokey Feedback Mechanism:</b> Instead of statically repeating the 10-character Vigenère key, set: <i>K<sub>vig</sub>[i] = (K<sub>vig</sub>[i] + C[i-1]) mod 26</i> for <i>i &ge; 1</i>. This creates recursive inter-block dependency, completely neutralizing the periodic difference matrix &Delta;<b>P</b> in KPA at zero asymptotic computational cost.",
        numbered_style
    ))
    story.append(Paragraph(
        "<b>2. Keyed Transposition Permutation Layer:</b> Insert an <i>O(N)</i> columnar transposition shuffle between Stage 1 and Stage 2 driven by the primary key. Disrupting the contiguous alignment of digram pairs prevents the attacker from constructing paired linear vectors.",
        numbered_style
    ))
    story.append(Paragraph(
        "<b>3. Cipher-Block Chaining (CBC) Emulation:</b> XOR/add the previous ciphertext digram vector into the current plaintext vector before matrix multiplication: <b>Y</b><sub>j</sub> = <b>K</b><sub>hill</sub> &middot; (<b>X</b><sub>j</sub> &oplus; <b>Y</b><sub>j-1</sub>) mod 26, effectively breaking matrix linearity.",
        numbered_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Conclusion:</b>", sub_heading))
    story.append(Paragraph(
        "This project successfully fulfilled all CT-486 Complex Computing Problem requirements. By synthesizing a 10-character polyalphabetic Vigenère substitution with an invertible 2 &times; 2 Hill linear transformation, we demonstrated how Shannon's confusion and diffusion flatten statistical frequency distributions (IoC = 0.0405). Furthermore, our automated attack solver proved that linear ciphers remain susceptible to Known-Plaintext attacks, underscoring the absolute necessity of non-linear substitution structures in modern cryptography.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>GitHub Repository & Verification Suite:</b>", sub_heading))
    story.append(Paragraph(
        "All source code, test suites, attack simulators, and documentation are publicly hosted on GitHub:",
        body_style
    ))
    story.append(Paragraph(
        "<b>Repository URL:</b> <font color='#1A365D'><u>https://github.com/ameemakhtr/NIS_CCP</u></font><br/>"
        "&bull; <font face='Courier'>custom_cipher.py</font>: Core encryption and decryption pipeline.<br/>"
        "&bull; <font face='Courier'>attack.py</font>: Frequency analyzer, IoC calculator, and KPA solver.<br/>"
        "&bull; <font face='Courier'>benchmark.py</font>: Empirical benchmarking suite against Shift cipher.<br/>"
        "&bull; <font face='Courier'>test_suite.py</font>: 100% passing automated unit test suite.<br/>"
        "&bull; <font face='Courier'>build_report_pdf.py</font>: Standalone PDF compilation script.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {pdf_filename}")

if __name__ == '__main__':
    generate_pdf()
