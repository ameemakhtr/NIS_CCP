import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, Preformatted, KeepTogether
)
from reportlab.platypus import tables
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import pypdf
from custom_cipher import CustomHybridCipher, add_padding

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 2.5 * cm
FRAME_WIDTH = PAGE_WIDTH - 2 * MARGIN
NAVY = colors.HexColor("#1F2A44")
RULE = colors.HexColor("#C8CCD4")
SHADE = colors.HexColor("#F4F5F7")

FONT_NAMES = ("Serif", "Serif-Bold", "Serif-Italic", "Serif-BoldItalic", "Mono")
FONT_FILES = (
    ("LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf", "LiberationSerif-Italic.ttf", "LiberationSerif-BoldItalic.ttf", "LiberationMono-Regular.ttf"),
    ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf", "cour.ttf"),
)
FONT_DIRS = (
    "C:/Windows/Fonts",
    os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/liberation",
)


def register_fonts():
    """Registers TrueType fonts, which reportlab embeds in the PDF."""
    for files in FONT_FILES:
        for folder in FONT_DIRS:
            paths = [os.path.join(folder, name) for name in files]
            if all(os.path.exists(path) for path in paths):
                for name, path in zip(FONT_NAMES, paths):
                    pdfmetrics.registerFont(TTFont(name, path))
                registerFontFamily("Serif", normal="Serif", bold="Serif-Bold", italic="Serif-Italic", boldItalic="Serif-BoldItalic")
                registerFontFamily("Mono", normal="Mono", bold="Mono", italic="Mono", boldItalic="Mono")
                tables.CellStyle.fontname = "Serif"  # table default, otherwise non-embedded Helvetica
                return
    raise SystemExit("Install Liberation Serif and Mono (or Times New Roman and Courier New) to build the report.")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs["initialFontName"] = "Serif"  # otherwise reportlab adds non-embedded Helvetica
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
            left, right = MARGIN, PAGE_WIDTH - MARGIN
            self.saveState()
            self.setFont("Serif", 9.5)
            self.setFillColor(colors.black)
            self.setStrokeColor(RULE)
            self.setLineWidth(0.6)

            # Header
            self.drawString(left, PAGE_HEIGHT - 46, "Complex Computing Problem Report | CT-486: Network and Information Security")
            self.line(left, PAGE_HEIGHT - 53, right, PAGE_HEIGHT - 53)

            # Footer
            self.line(left, 53, right, 53)
            self.drawRightString(right, 40, f"Page {self._pageNumber} of {page_count}")
            self.drawString(left, 40, "Department of Computer Science & IT, NED University")
            self.restoreState()


class ReportDocument(BaseDocTemplate):
    INDEXED_STYLES = {
        "SectionHeading": ("TOCEntry", 0),
        "SubHeading": ("TOCEntry", 1),
        "FigureCaption": ("ListOfFigures", 0),
        "TableCaption": ("ListOfTables", 0),
    }

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in self.INDEXED_STYLES:
            kind, level = self.INDEXED_STYLES[flowable.style.name]
            text = flowable.getPlainText()
            key = f"{kind}:{text}"
            self.canv.bookmarkPage(key)
            self.notify(kind, (level, text, self.page, key))


class CaptionList(TableOfContents):
    """A table of contents fed by figure or table captions instead of headings."""

    def __init__(self, kind, **kwargs):
        super().__init__(**kwargs)
        self.kind = kind

    def notify(self, kind, stuff):
        if kind == self.kind:
            self.addEntry(*stuff)


def build_pdf():
    register_fonts()
    pdf_filename = os.path.join(SCRIPT_DIR, "Complex_Computing_Problem_Report.pdf")
    doc = ReportDocument(
        pdf_filename,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="Complex Computing Problem Report: CT-486 Network and Information Security",
        author="Team Entropy",
    )
    frame = Frame(MARGIN, MARGIN, FRAME_WIDTH, PAGE_HEIGHT - 2 * MARGIN, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame])])

    styles = getSampleStyleSheet()

    # Cover page typography
    title_style = ParagraphStyle('CoverTitle', parent=styles['Normal'], fontName='Serif-Bold', fontSize=24, leading=28, alignment=1, textColor=NAVY)
    subtitle_style = ParagraphStyle('CoverSubtitle', parent=styles['Normal'], fontName='Serif-Bold', fontSize=15, leading=19, alignment=1, textColor=NAVY)
    dept_style = ParagraphStyle('CoverDept', parent=styles['Normal'], fontName='Serif', fontSize=12.5, leading=16.5, alignment=1, textColor=colors.black)
    cover_text = ParagraphStyle('CoverText', parent=styles['Normal'], fontName='Serif', fontSize=9.5, leading=13.5, spaceAfter=5, textColor=colors.black)

    # Body typography
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Normal'], fontName='Serif-Bold', fontSize=14, leading=17, spaceBefore=14, spaceAfter=6, textColor=NAVY, keepWithNext=1)
    front_heading = ParagraphStyle('FrontHeading', parent=section_heading)
    sub_heading = ParagraphStyle('SubHeading', parent=styles['Normal'], fontName='Serif-Bold', fontSize=12, leading=15, spaceBefore=9, spaceAfter=4, textColor=NAVY, keepWithNext=1)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Serif', fontSize=11, leading=12.65, spaceAfter=6, alignment=4, textColor=colors.black, allowWidows=0, allowOrphans=0)
    bullet_style = ParagraphStyle('BulletStyle', parent=body_style, leftIndent=14, firstLineIndent=-9, spaceAfter=4)
    reference_style = ParagraphStyle('Reference', parent=body_style, leftIndent=24, firstLineIndent=-24, alignment=0)
    code_style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontName='Mono', fontSize=9, leading=11, textColor=colors.black)
    table_caption = ParagraphStyle('TableCaption', parent=styles['Normal'], fontName='Serif-Italic', fontSize=10, leading=12, spaceAfter=4, alignment=1, textColor=colors.black)
    figure_caption = ParagraphStyle('FigureCaption', parent=table_caption, spaceBefore=4, spaceAfter=10)
    table_header = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Serif-Bold', fontSize=9.5, leading=11, alignment=1, textColor=colors.white)
    contents_level_0 = ParagraphStyle('Contents0', parent=styles['Normal'], fontName='Serif', fontSize=11, leading=14)
    contents_level_1 = ParagraphStyle('Contents1', parent=contents_level_0, leftIndent=16)

    story = []

    # =========================================================
    # COVER PAGE
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
        [Paragraph("<b>Mr. Ameem Akhtar</b> .........................................................", cover_text), Paragraph("<b>(CR-23013)</b>", cover_text)],
        [Paragraph("<b>Mr. Minhal Rizvi</b> .........................................................", cover_text), Paragraph("<b>(CR-23017)</b>", cover_text)],
        [Paragraph("<b>Mr. Muhammad Usman</b> .....................................................", cover_text), Paragraph("<b>(CR-23038)</b>", cover_text)],
        [Paragraph("<b>Mr. Maaz Wasim</b> .........................................................", cover_text), Paragraph("<b>(CR-23041)</b>", cover_text)],
    ]
    t_members = Table(members_data, colWidths=[3.8*inch, 1.8*inch])
    t_members.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_members)

    story.append(Spacer(1, 34))
    story.append(Paragraph("<b>Submitted to:</b> Prof. Dr. Shariq Mahmood Khan (Professor, Department of CS & IT)", cover_text))
    story.append(Paragraph("<b>Submission Date:</b> November 08, 2026", cover_text))
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

    def add_table(caption, data, widths):
        scale = FRAME_WIDTH / sum(widths)
        cells = [[Paragraph(text, table_header) for text in data[0]]] + data[1:]
        table = Table(cells, colWidths=[w * scale for w in widths], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('FONTNAME', (0,0), (-1,-1), 'Serif'),
            ('FONTSIZE', (0,0), (-1,-1), 9.5),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, RULE),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SHADE])
        ]))
        story.append(KeepTogether([Paragraph(caption, table_caption), table, Spacer(1, 10)]))

    def add_figure(filename, caption):
        path = os.path.join(SCRIPT_DIR, filename)
        pixel_width, pixel_height = ImageReader(path).getSize()
        image = RLImage(path, width=FRAME_WIDTH, height=FRAME_WIDTH * pixel_height / pixel_width)
        story.append(KeepTogether([image, Paragraph(caption, figure_caption)]))

    def add_code(text):
        table = Table([[Preformatted(text, code_style)]], colWidths=[FRAME_WIDTH])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), SHADE),
            ('BOX', (0,0), (-1,-1), 0.75, RULE),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 6))

    def add_text(text, style=body_style):
        # Smaller, shallower subscripts so they clear the line below; inline code matched to the serif's visual size
        text = text.replace("<sub>", "<sub rise='2' size='8'>").replace("<font face='Mono'>", "<font face='Mono' size='9.5'>")
        story.append(Paragraph(text, style))

    def add_section(text):
        story.append(Paragraph(text, section_heading))

    def add_sub(text):
        story.append(Paragraph(text, sub_heading))

    # =========================================================
    # FRONT MATTER
    # =========================================================
    add_section("Abstract")
    add_text("This report presents the design, implementation and cryptanalysis of a custom two-stage classical cipher developed for the CT-486 Complex Computing Problem. The first stage is a Vigenere cipher with a key of at least 10 letters, and the second stage is a 2 × 2 Hill cipher applied to pairs of letters modulo 26. The cipher encrypts and decrypts A-Z messages of different lengths in linear time, at a constant-factor cost over a single-stage Shift cipher. Frequency analysis shows that the design hides English single-letter statistics well. However, both stages are linear, so their composition is a single affine Hill cipher with a repeating constant term. A known-plaintext attack exploits this by searching all 157,248 invertible matrices and reading off the Vigenere key. Without being given either key or the key length, the attack recovers the complete message in about one second when the attacker knows at least L + 20 letters, where L is the key length. The main conclusion is that combining two linear classical ciphers hides letter frequencies but adds little resistance to a known-plaintext attack.")
    story.append(PageBreak())

    contents_rows = TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ])
    contents_styles = {"levelStyles": [contents_level_0, contents_level_1], "tableStyle": contents_rows, "dotsMinLevel": 0, "rightColumnWidth": 40}
    story.append(Paragraph("Table of Contents", front_heading))
    story.append(TableOfContents(**contents_styles))
    story.append(Paragraph("List of Figures", front_heading))
    story.append(CaptionList("ListOfFigures", **contents_styles))
    story.append(Paragraph("List of Tables", front_heading))
    story.append(CaptionList("ListOfTables", **contents_styles))
    story.append(PageBreak())

    # =========================================================
    # SECTION 1: PROBLEM AND DESIGN OVERVIEW
    # =========================================================
    add_section("1. Problem Statement and Design Overview")
    add_text("The brief asks for a custom cipher built from at least two classical ciphers, in at least two stages that each use a different technique, with a key of at least 10 characters; a program that encrypts and decrypts A-Z text of different lengths; an attack that breaks the cipher; and an analysis of its efficiency against a single-stage Shift cipher.")
    add_text("This project combines a <b>Vigenere cipher</b> (polyalphabetic substitution) [4] with a <b>2 × 2 Hill cipher</b> (polygraphic matrix transformation over Z<sub>26</sub>) [2]. It is implemented in Python (<font face='Mono'>custom_cipher.py</font>), and the attack is a <b>known-plaintext attack</b> (<font face='Mono'>attack.py</font>). The main result is that the second stage hides letter frequencies well but adds little real security: both stages are linear, and the combination is broken in about a second by an attacker who knows roughly 40 letters of a message.")

    add_sub("1.1 Mathematical Definition")
    add_text("Letters map to A=0, ..., Z=25. The padded plaintext P is encrypted with a Vigenere key K<sub>vig</sub> of length L ≥ 10 and an invertible matrix K<sub>hill</sub> = [[a, b], [c, d]]:")
    add_code(
        "Stage 1 (Vigenere):  C1[i] = (P[i] + Kvig[i mod L]) mod 26\n"
        "Stage 2 (Hill):      [C[2j], C[2j+1]]^T = Khill * [C1[2j], C1[2j+1]]^T mod 26"
    )
    add_text("Stage 2 can be undone only if gcd(det K<sub>hill</sub>, 26) = 1, that is, the determinant Δ = (ad - bc) mod 26 is neither even nor a multiple of 13. Decryption uses K<sub>hill</sub><sup>-1</sup> = Δ<sup>-1</sup> · [[d, -b], [-c, a]] mod 26. There are |GL(2, Z<sub>26</sub>)| = 157,248 such matrices.")

    add_sub("1.2 How the Classical Techniques Are Combined")
    bullets = [
        "<b>Keys.</b> The cipher takes two keys, each at least 10 letters after removing non-letters; shorter keys are rejected. The Vigenere key is used letter by letter. The Hill phrase is reduced to a matrix by adding each of its letters, in turn, into entry a, b, c or d mod 26, so every letter of the phrase affects the matrix. If the determinant is not invertible, entry d is incremented (carrying into c, b, a) until it is.",
        "<b>Order of the stages.</b> Vigenere runs first because it needs to act on individual letters at known positions. Its output is cut into pairs and each pair is multiplied by the Hill matrix, so each ciphertext letter depends on two Vigenere-shifted letters and on the key letters at both positions.",
        "<b>What each stage contributes.</b> Vigenere replaces one fixed alphabet with L alphabets, which flattens the letter histogram. Hill then mixes neighbouring letters, which hides the repeating key alphabet from column-by-column Vigenere analysis, since a ciphertext letter no longer belongs to a single Caesar alphabet.",
        "<b>Padding.</b> Hill needs an even number of letters. An odd-length message gets 'X' and an even-length message gets 'XA'. Padding is always added so that decryption can remove it without guessing: a final 'X' means one padding letter, anything else means two. A message genuinely ending in X, such as FOXX, therefore decrypts exactly.",
    ]
    for bullet in bullets:
        add_text("• " + bullet, bullet_style)

    example = CustomHybridCipher("CRYPTOGRAPHYKEY", "HILLCIPHERKEY")
    padded = add_padding("ATTACKATDAWN")
    stage1 = "".join(chr(n + 65) for n in example._vigenere_encrypt(padded))
    add_sub("1.3 Worked Example")
    add_code(
        f"Keys:        Kvig = CRYPTOGRAPHYKEY (L = 15), Hill phrase = HILLCIPHERKEY\n"
        f"Matrix:      Khill = {[list(example.hill_mat[:2]), list(example.hill_mat[2:])]}\n"
        f"Plaintext:   ATTACKATDAWN\n"
        f"Padded:      {padded}\n"
        f"Stage 1:     {stage1}\n"
        f"Stage 2:     {example.encrypt('ATTACKATDAWN')}   (final ciphertext)\n"
        f"Decrypted:   {example.decrypt(example.encrypt('ATTACKATDAWN'))}"
    )

    # =========================================================
    # SECTION 2: ALGORITHMS
    # =========================================================
    add_section("2. Encryption and Decryption Algorithms")
    add_sub("2.1 Algorithm 1: Encryption")
    add_code(
        "Input:  Plaintext P, Vigenere key Kvig (|Kvig| >= 10),\n"
        "        Hill phrase H (|H| >= 10)\n"
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
    add_sub("2.2 Algorithm 2: Decryption")
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
    add_sub("2.3 DeriveMatrix(H)")
    add_code(
        "1: [a, b, c, d] <- [0, 0, 0, 0]\n"
        "2: for i = 0 to |H| - 1 do  entry[i mod 4] <- (entry[i mod 4] + H[i]) mod 26\n"
        "3: while gcd(ad - bc, 26) != 1 do  increment d, carrying into c, b, a at 26\n"
        "4: return [[a, b], [c, d]]"
    )
    add_text("The unit tests in <font face='Mono'>test_suite.py</font> check exact round trips for every length from 1 to 26, a 380-letter message, and padding-like endings such as X, XX, XA and FOXX.")

    # =========================================================
    # SECTION 3: SECURITY ANALYSIS
    # =========================================================
    add_section("3. Security Analysis")
    add_sub("3.1 Key Space")
    add_text("With L = 10 there are 26<super>10</super> × 157,248 ≈ 2.2 × 10<super>19</super> key pairs, against 26 for the Shift cipher, so exhaustive search of both keys together is impractical. This number overstates the security, because the attack in Section 4 never searches the Vigenere key: it searches the matrices alone and solves for the Vigenere key directly.")
    add_sub("3.2 Structure")
    add_text("Substituting Stage 1 into Stage 2 gives C<sub>j</sub> = K<sub>hill</sub> · P<sub>j</sub> + K<sub>hill</sub> · V<sub>j</sub> mod 26, where V<sub>j</sub> is the pair of key letters at block j. The whole cipher is therefore a single affine Hill cipher whose constant term repeats with the key. Composing two linear stages does not create a stronger kind of function, and that is the weakness the attack exploits.")
    add_sub("3.3 Confusion and Diffusion")
    add_text(f"In the terms introduced by Shannon [1], Vigenere provides confusion: the same letter encrypts differently at different positions. Diffusion is limited to one pair. Changing one plaintext letter changed <b>{freq['avg_ciphertext_letters_changed']}</b> ciphertext letters on average and never more than {freq['max_ciphertext_letters_changed']}, whereas a modern block cipher changes about half of its output.")
    add_sub("3.4 Frequency Analysis")
    add_text(f"Letter counts of each ciphertext were compared with the expected English distribution, using the Index of Coincidence [3], IoC = ∑ f<sub>i</sub>(f<sub>i</sub> - 1) / [N(N - 1)], and the chi-squared distance from English. Figures are averages over {freq['samples']} random key sets and {freq['length']:,}-letter passages of English technical documentation, which runs slightly above the textbook English IoC of 0.0667. Table 1 lists the results and Figure 1 plots them.")
    rows = [["Text", "Mean IoC", "Std. dev.", "Chi-squared vs English"]]
    for name in ["Plaintext", "Shift", "Hill only", "Vigenere only", "Custom"]:
        label = {"Custom": "Custom (Vigenere + Hill)", "Shift": "Shift ciphertext"}.get(name, name)
        rows.append([label, f"{stats[name]['ioc']:.4f}", f"{stats[name]['ioc_stdev']:.4f}", f"{stats[name]['chi_squared']:,.1f}"])
    add_table("Table 1: Measured letter statistics of each text against English", rows, [2.3, 1.2, 1.2, 1.8])
    add_figure("frequency_ioc_analysis.png", "Figure 1: Measured letter frequency of each ciphertext against expected English, and measured IoC.")
    add_text(f"The Shift cipher has exactly the plaintext's IoC ({stats['Shift']['ioc']:.4f}) because it only renames letters. The custom cipher reaches {stats['Custom']['ioc']:.4f}, close to the uniform value of 0.0385, and its histogram no longer resembles English. The chi-squared value shows only that the ciphertext is far from English. Frequency analysis on its own therefore does not recover the key here, so it serves as a measure of how well the statistics are hidden; the cipher is broken by the attack below.")

    # =========================================================
    # SECTION 4: ATTACK
    # =========================================================
    add_section("4. Attack Method and Results")
    add_sub("4.1 Scenario")
    add_text("The attacker has the whole ciphertext and the plaintext of its first M letters, such as a predictable message header, and knows the algorithm and that keys have at least 10 letters. The attacker does <b>not</b> know either key or the Vigenere key length.")
    add_sub("4.2 Algorithm 3: Known-Plaintext Attack")
    add_code(
        "Input:  Ciphertext C, known plaintext P[0..M-1]\n"
        "Output: Khill, Kvig and the full plaintext, or failure\n"
        " 1: Pool <- all 157,248 invertible 2x2 matrices mod 26 with their inverses\n"
        " 2: for L = 10 to M - 20 do                       // candidate key lengths\n"
        " 3:     for each matrix K in Pool do\n"
        " 4:         for each known pair j do\n"
        " 5:             [x1, x2]^T <- Kinv * [C[2j], C[2j+1]]^T mod 26\n"
        " 6:             k <- (x - P) mod 26 for both letters\n"
        " 7:             if k disagrees with a key letter already set at i mod L\n"
        "                then reject K\n"
        " 8:         if K was not rejected then decrypt all of C with (K, k); return\n"
        " 9: return failure"
    )
    add_sub("4.3 Why It Works")
    add_text("Once the correct matrix is guessed, Stage 2 is undone and Stage 1 reduces to k[i] = x[i] - P[i], which directly reveals the Vigenere key. A wrong matrix produces a stream that does not repeat every L letters. The check exploits exactly the two properties identified in Section 3: linearity and the repeating key. Known pairs are tested grouped by key position, so a wrong matrix is usually rejected after a few checks.")
    add_sub("4.4 How Much Known Text Is Needed")
    add_text("At least L letters are needed to see every key letter, and extra letters are needed to reject wrong matrices. Because 26 = 2 × 13, a matrix that is correct mod 13 and wrong only mod 2 passes each check about half the time. In a separate experiment (<font face='Mono'>false_match_experiment.py</font>) with L = 20, 8 extra letters returned a wrong key in 14 of 150 runs and 20 extra letters in 0 of 150, so the attack requires M ≥ L + 20 and reports failure otherwise.")
    add_sub("4.5 Results")
    add_text(f"Table 2 varies the ciphertext length and Table 3 varies the amount of known plaintext. Each row is {trials} trials, each with new random keys (Vigenere key of 10 to 20 letters) and a new random English passage. A trial counts as a success only if the complete message is recovered exactly. Time excludes the one-off construction of the matrix pool, which took {results['gl2_precompute_ms']:.0f} ms.")
    rows = [["Ciphertext length", "Known letters", "Success rate", "Average time (ms)", "Worst time (ms)", "Average matrices tried"]]
    for row in by_length:
        rows.append([f"{row['length']:,}", f"{row['known_chars']:,}", f"{row['success_rate']:.1f}%", f"{row['avg_time_ms']:.1f}", f"{row['max_time_ms']:.1f}", f"{row['avg_matrices']:,}"])
    add_table("Table 2: Success and effort by ciphertext length (first 25% of the message known)", rows, [1.2, 0.95, 0.95, 1.15, 1.05, 1.2])
    rows = [["Known letters", "Success rate", "Average time (ms)", "Worst time (ms)", "Average matrices tried"]]
    for row in by_known:
        rows.append([f"{row['known_chars']}", f"{row['success_rate']:.1f}%", f"{row['avg_time_ms']:.1f}", f"{row['max_time_ms']:.1f}", f"{row['avg_matrices']:,}"])
    add_table("Table 3: Success and effort by amount of known plaintext (1,000-letter ciphertext)", rows, [1.2, 1.2, 1.4, 1.3, 1.4])
    add_text(f"Success is decided by the amount of known text, not by the ciphertext length as such. Short messages fail in Table 2 only because 25% of them is too few letters. With 40 or more known letters, enough for the longest key tested, recovery was exact in every trial. When recovery succeeded, the attack averaged about {typical_ms:.0f} ms and at most {worst_ms:.0f} ms, and its cost did not grow with the ciphertext length.")

    # =========================================================
    # SECTION 5: PERFORMANCE
    # =========================================================
    add_section("5. Performance and Efficiency")
    add_sub("5.1 Time Complexity")
    add_text("For a message of N letters:")
    for bullet in [
        "<b>Encryption:</b> Vigenere does N additions and Hill does N/2 matrix multiplications of constant size, so the total is <b>O(N)</b>.",
        "<b>Decryption:</b> inverting a 2 × 2 matrix takes constant time, followed by the same two passes in reverse, so the total is <b>O(N)</b>.",
        "<b>Shift cipher:</b> one addition per letter, also <b>O(N)</b>. All three use O(N) space. The custom cipher is slower by a constant factor only.",
        "<b>Attack:</b> the matrix pool is a one-off 26<super>4</super> = 456,976 determinant checks. The search is O(T · |GL| · c), where T is the number of key lengths tried, |GL| = 157,248 and c is the average number of checks before rejection, which is small and in the worst case M. Recovering the message afterwards is O(N).",
    ]:
        add_text("• " + bullet, bullet_style)
    add_sub("5.2 Measured Performance")
    add_text("Table 4 gives the measured cipher times, and Figure 2 plots them beside the attack success rates of Table 3.")
    environment = results["environment"]
    rows = [["Length", "Custom encrypt", "Custom decrypt", "Shift encrypt", "Shift decrypt", "Encrypt overhead", "Custom letters/s"]]
    for row in cipher_rows:
        rows.append([f"{row['length']:,}", f"{row['custom_enc_ms']:.4f}", f"{row['custom_dec_ms']:.4f}", f"{row['shift_enc_ms']:.4f}", f"{row['shift_dec_ms']:.4f}", f"{row['custom_enc_ms'] / row['shift_enc_ms']:.2f}x", f"{row['length'] / row['custom_enc_ms'] * 1000:,.0f}"])
    add_table(f"Table 4: Measured cipher time in ms (average of 50 runs, Python {environment['python']})", rows, [0.7, 1.0, 1.0, 0.9, 0.9, 1.0, 1.0])
    add_figure("benchmark_comparison.png", "Figure 2: Measured cipher time against message length, and attack success against known plaintext.")
    add_text(f"Time grows linearly with length for both ciphers, as the analysis predicts. Encrypting 1,000 letters took {at_1000['custom_enc_ms']:.3f} ms with the custom cipher and {at_1000['shift_enc_ms']:.3f} ms with the Shift cipher. The two-stage design costs {min(overheads):.1f}x to {max(overheads):.1f}x the time of the single-stage cipher, and in return it hides letter frequencies that the Shift cipher exposes completely. These are timings of interpreted Python on one machine, so the ratios are more meaningful than the absolute values.")

    # =========================================================
    # SECTION 6: IMPROVEMENTS
    # =========================================================
    add_section("6. Improving Security Without Significantly Increasing Complexity")
    add_text("The attack depends on linearity and on the repeating key, so useful changes must remove one of these. Each option below stays O(N). They would raise the attacker's cost but were not implemented or measured here, and none would make the cipher secure by modern standards.")
    for bullet in [
        "<b>1. Keyed non-linear substitution between the stages.</b> Pass each Vigenere output letter through a secret permutation of the alphabet, one table lookup per letter. The relation k[i] = x[i] - P[i] then no longer holds, so the key letters cannot be read off after guessing the matrix.",
        "<b>2. Keyed columnar transposition between the stages.</b> Reordering letters by a secret permutation separates known plaintext from the ciphertext positions it produces, so the attacker must also search the permutation.",
        "<b>3. A non-repeating keystream.</b> Derive a different Vigenere key for each message from the main key and a per-message value. The periodicity check that rejects wrong matrices then has nothing to test.",
    ]:
        add_text(bullet, bullet_style)
    add_text("Two changes that seem helpful are weak on their own. A longer Vigenere key only raises the known text needed (M ≥ L + 20). A larger Hill matrix leaves the system linear: subtracting blocks a whole number of key periods apart cancels the Vigenere term and gives ΔC = K<sub>hill</sub> · ΔP, which can be solved with linear algebra rather than search.")

    # =========================================================
    # SECTION 7: CODE
    # =========================================================
    add_section("7. Code Submission")
    add_text("The source code, tests and measurement scripts are at: <b><u>https://github.com/ameemakhtr/NIS_CCP</u></b>. Running <font face='Mono'>python benchmark.py</font> reproduces <font face='Mono'>results.json</font>, from which every table and figure above is generated.")
    add_text("<b>Code Availability.</b> The repository is available at https://github.com/ameemakhtr/NIS_CCP, and the project is run with these commands:")
    add_code(
        "python test_suite.py\n"
        "python main.py --demo\n"
        "python benchmark.py"
    )

    # =========================================================
    # SECTION 8: CONCLUSION
    # =========================================================
    add_section("8. Conclusion")
    add_text(f"This project built a two-stage classical cipher that combines a Vigenere cipher with a 2 × 2 Hill cipher, together with a program for encryption and decryption and an attack on the design. The cipher hides single-letter statistics, bringing the Index of Coincidence to about {stats['Custom']['ioc']:.3f}. Both stages are linear, however, so a known-plaintext attack recovers both keys in about a second given at least L + 20 known letters. This shows that combining two linear classical ciphers adds little security against an attacker who knows part of a message. The improvements in Section 6 would raise the cost of this attack.")

    # =========================================================
    # REFERENCES
    # =========================================================
    add_section("References")
    for reference in [
        "[1]\u2003C. E. Shannon, \"Communication Theory of Secrecy Systems,\" <i>Bell System Technical Journal</i>, vol. 28, no. 4, pp. 656-715, 1949.",
        "[2]\u2003L. S. Hill, \"Cryptography in an Algebraic Alphabet,\" <i>The American Mathematical Monthly</i>, vol. 36, no. 6, pp. 306-312, 1929.",
        "[3]\u2003W. F. Friedman, \"The Index of Coincidence and Its Applications in Cryptography,\" Riverbank Publication No. 22, 1922.",
        "[4]\u2003W. Stallings, <i>Cryptography and Network Security: Principles and Practice</i>, 8th ed. Pearson, 2020.",
    ]:
        add_text(reference, reference_style)

    doc.multiBuild(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {pdf_filename}")

if __name__ == '__main__':
    build_pdf()
