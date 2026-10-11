import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Devanagari font
FONT_REGULAR = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"

has_devanagari = os.path.exists(FONT_REGULAR) and os.path.exists(FONT_BOLD)
if has_devanagari:
    pdfmetrics.registerFont(TTFont("Devanagari", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("Devanagari-Bold", FONT_BOLD))
    main_font = "Devanagari"
    main_font_bold = "Devanagari-Bold"
else:
    main_font = "Helvetica"
    main_font_bold = "Helvetica-Bold"

def generate_pdf(output_filename="Sanskrit_POS_Expert_Manual.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName=main_font_bold,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1, # Center
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName=main_font,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        fontName=main_font_bold,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        fontName=main_font_bold,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        fontName=main_font,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        fontName=main_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#92400e')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName=main_font_bold,
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName=main_font,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName=main_font_bold,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Sanskrit POS Annotation & Verification Portal", title_style))
    story.append(Paragraph("Official User Guide & Workflow Manual for Sanskrit Language Scholars", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=12))

    # 1. Project Overview & URL
    story.append(Paragraph("1. Quick Access & Credentials", h1_style))
    intro_p = (
        "This portal is developed for an M.Tech Data Science dissertation on <b>Cross-Domain Sanskrit POS Tagging</b>. "
        "Your expert linguistic verification will establish the gold-standard dataset for the news domain. "
        "The application is accessible from any phone, tablet, or laptop browser without installing any software."
    )
    story.append(Paragraph(intro_p, body_style))

    # Access Info Table
    access_data = [
        [Paragraph("<b>Portal URL</b>", table_cell_bold), Paragraph("<b>https://sanskrit-pos-annotation-app.vercel.app/</b>", table_cell_style)],
        [Paragraph("<b>Username</b>", table_cell_bold), Paragraph("<b>sanskrit_scholar</b> (Pre-configured expert account)", table_cell_style)],
        [Paragraph("<b>Password</b>", table_cell_bold), Paragraph("<b>password123</b>", table_cell_style)],
        [Paragraph("<b>Supported Devices</b>", table_cell_bold), Paragraph("Laptops, Desktops, iPads/Tablets, Mobile Phones (Chrome, Safari, Firefox)", table_cell_style)]
    ]
    t_access = Table(access_data, colWidths=[1.8*inch, 5.2*inch])
    t_access.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_access)
    story.append(Spacer(1, 10))

    # 2. Step-by-Step Workflow
    story.append(Paragraph("2. Annotation Interface & Workflow", h1_style))
    workflow_steps = (
        "<b>Step 1 — Log In:</b> Open the URL and sign in using the credentials above.<br/>"
        "<b>Step 2 — Open Sentence:</b> On the dashboard, click <b>'▶ Resume Annotation'</b>. The system automatically loads your next pending sentence.<br/>"
        "<b>Step 3 — Review Text:</b> Read the complete original Sanskrit sentence in Devanagari script.<br/>"
        "<b>Step 4 — Review Tokens:</b> Each token is listed with its automated Stanza UPOS prediction (for reference only) and morphological features.<br/>"
        "<b>Step 5 — Assign Sanskrit POS Tag:</b> Select the correct Consortium tag from the dropdown menu for every token.<br/>"
        "<b>Step 6 — Finalize:</b> Click <b>'Save & Next'</b> to verify and advance to the next sentence."
    )
    story.append(Paragraph(workflow_steps, body_style))

    # 3. Save Draft vs Save & Next
    story.append(Paragraph("3. Understanding 'Save Draft' vs. 'Save & Next'", h1_style))
    
    actions_data = [
        [
            Paragraph("<b>Action</b>", table_header_style),
            Paragraph("<b>When to Use</b>", table_header_style),
            Paragraph("<b>System Behavior</b>", table_header_style)
        ],
        [
            Paragraph("<b>💾 Save Draft</b>", table_cell_bold),
            Paragraph("When taking a break or partially completing a sentence.", table_cell_style),
            Paragraph("Saves selected tags securely. Sets status to <i>In Progress</i>. Does <b>not</b> count as verified. Restores your work upon return.", table_cell_style)
        ],
        [
            Paragraph("<b>✓ Save & Next</b>", table_cell_bold),
            Paragraph("When <b>all tokens</b> in the sentence have an assigned tag.", table_cell_style),
            Paragraph("Validates completeness. Atomically commits all tags. Marks sentence as <i>Verified</i> with your username and timestamp. Loads next pending sentence automatically.", table_cell_style)
        ]
    ]
    t_actions = Table(actions_data, colWidths=[1.4*inch, 2.4*inch, 3.2*inch])
    t_actions.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_actions)
    story.append(Spacer(1, 10))

    # 4. What happens if you miss a word
    story.append(Paragraph("4. Critical Safety Guard: What Happens If You Miss a Word?", h1_style))
    
    warning_box_text = (
        "<b>DATA INTEGRITY SAFETY RULE:</b><br/>"
        "If you accidentally miss any token and click <b>'Save & Next'</b>:<br/>"
        "• <b>The system will BLOCK the submission.</b> It will never save an incomplete sentence as verified.<br/>"
        "• <b>A clear alert appears:</b> <i>'Cannot verify sentence: Missing approved POS tags for tokens: #3, #7. Please assign all tags before clicking Save & Next.'</i><br/>"
        "• <b>Visual Highlighting:</b> The missing words remain highlighted in <b>amber/gold</b> with <i>'-- Select Tag --'</i>.<br/>"
        "• <b>Nothing is lost:</b> All your other selections stay completely intact on screen. Simply choose the tag for the highlighted words and click <b>Save & Next</b> again!"
    )
    t_warn = Table([[Paragraph(warning_box_text, callout_style)]], colWidths=[7.0*inch])
    t_warn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffbeb')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#f59e0b')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_warn)
    story.append(Spacer(1, 12))

    # Page Break for Tag Table
    story.append(PageBreak())

    # 5. Tag Inventory Reference Table
    story.append(Paragraph("5. Sanskrit Consortium POS Tag Inventory (23 Approved Tags)", h1_style))
    story.append(Paragraph("Assign strictly one approved tag code from this table to each Sanskrit token:", body_style))

    tag_rows = [
        [
            Paragraph("<b>Tag</b>", table_header_style),
            Paragraph("<b>Sanskrit Name</b>", table_header_style),
            Paragraph("<b>English Meaning / Syntactic Function</b>", table_header_style),
            Paragraph("<b>Sanskrit Example</b>", table_header_style)
        ],
        [Paragraph("<b>N</b>", table_cell_bold), Paragraph("नामपदम्", table_cell_style), Paragraph("General noun stem or inflected noun", table_cell_style), Paragraph("विद्या, छात्रेण, मतिः", table_cell_style)],
        [Paragraph("<b>NS</b>", table_cell_bold), Paragraph("विशेषनाम", table_cell_style), Paragraph("Proper noun (person, city, entity)", table_cell_style), Paragraph("नरेन्द्रमोदी, नवदेहल्याम्", table_cell_style)],
        [Paragraph("<b>NV</b>", table_cell_bold), Paragraph("कृदन्तरूपम्", table_cell_style), Paragraph("Verbal noun / Krudanta participle", table_cell_style), Paragraph("गमनम्, उद्घाटितवान्", table_cell_style)],
        [Paragraph("<b>KNV</b>", table_cell_bold), Paragraph("तद्धितान्तरूपम्", table_cell_style), Paragraph("Secondary derivative / Taddhita noun", table_cell_style), Paragraph("भारतीयः, धार्मिकम्", table_cell_style)],
        [Paragraph("<b>SN</b>", table_cell_bold), Paragraph("सर्वनाम", table_cell_style), Paragraph("Pronoun (personal, demonstrative)", table_cell_style), Paragraph("अहम्, तत्, एषः, अस्याः", table_cell_style)],
        [Paragraph("<b>SNV</b>", table_cell_bold), Paragraph("सर्वनाम-विशेषणम्", table_cell_style), Paragraph("Pronominal adjective modifying a noun", table_cell_style), Paragraph("<b>तस्मिन्</b> वने, <b>सर्वे</b> जनाः", table_cell_style)],
        [Paragraph("<b>SNS</b>", table_cell_bold), Paragraph("समस्तसर्वनाम", table_cell_style), Paragraph("Pronominal member inside a compound", table_cell_style), Paragraph("मत्प्रिय, तत्सदृश", table_cell_style)],
        [Paragraph("<b>SAM</b>", table_cell_bold), Paragraph("पूर्वपदम्", table_cell_style), Paragraph("Compound initial member", table_cell_style), Paragraph("<b>राम</b>लक्ष्मणौ (राम)", table_cell_style)],
        [Paragraph("<b>SAMY</b>", table_cell_bold), Paragraph("मध्यपदम्", table_cell_style), Paragraph("Compound middle member", table_cell_style), Paragraph("धर्म<b>कर्म</b>विपाकः", table_cell_style)],
        [Paragraph("<b>SAMP</b>", table_cell_bold), Paragraph("उत्तरपदम्", table_cell_style), Paragraph("Compound final inflected member", table_cell_style), Paragraph("राम<b>लक्ष्मणौ</b> (लक्ष्मणौ)", table_cell_style)],
        [Paragraph("<b>KP</b>", table_cell_bold), Paragraph("क्रियापदम् / तिङन्तम्", table_cell_style), Paragraph("Finite verb with tense/mood and person", table_cell_style), Paragraph("वर्तते, भवति, उद्घाटितवान्", table_cell_style)],
        [Paragraph("<b>UP</b>", table_cell_bold), Paragraph("उपसर्गः", table_cell_style), Paragraph("Verbal prefix standing separately", table_cell_style), Paragraph("प्र, सम्, अनु, वि", table_cell_style)],
        [Paragraph("<b>AVN</b>", table_cell_bold), Paragraph("सामान्य-अव्ययम्", table_cell_style), Paragraph("Indeclinable particle / Punctuation", table_cell_style), Paragraph("च, अपि, एव, तथा, ।, ?", table_cell_style)],
        [Paragraph("<b>AVP</b>", table_cell_bold), Paragraph("क्रियाविशेषणम्", table_cell_style), Paragraph("Adverbial indeclinable modifying a verb", table_cell_style), Paragraph("सर्वदा, सर्वथा, अद्य, शनैः", table_cell_style)],
        [Paragraph("<b>AVUP</b>", table_cell_bold), Paragraph("सोपसर्ग-अव्ययम्", table_cell_style), Paragraph("Indeclinable prefixed with upasarga", table_cell_style), Paragraph("प्रत्यहम्, यथाशक्ति", table_cell_style)],
        [Paragraph("<b>SAMB</b>", table_cell_bold), Paragraph("संयोजकम् / सम्बन्धकः", table_cell_style), Paragraph("Conjunction (coordinating/subordinating)", table_cell_style), Paragraph("यतः, तथापि, यद्यपि, चेत्", table_cell_style)],
        [Paragraph("<b>AVU</b>", table_cell_bold), Paragraph("विस्मयादिबोधकम्", table_cell_style), Paragraph("Interjection / Exclamatory particle", table_cell_style), Paragraph("अहो, हा, हन्त, भोः", table_cell_style)],
        [Paragraph("<b>K</b>", table_cell_bold), Paragraph("कर्मप्रवचनीयः", table_cell_style), Paragraph("Governing prepositional particle", table_cell_style), Paragraph("प्रति, अनु, अन्तरेण", table_cell_style)],
        [Paragraph("<b>AKV</b>", table_cell_bold), Paragraph("सहायक्रिया", table_cell_style), Paragraph("Secondary / Auxiliary verb form", table_cell_style), Paragraph("अस्ति (when auxiliary)", table_cell_style)],
        [Paragraph("<b>AB</b>", table_cell_bold), Paragraph("संक्षेपः", table_cell_style), Paragraph("Abbreviated word or symbol", table_cell_style), Paragraph("डॉ., पं., सं.", table_cell_style)],
        [Paragraph("<b>AVC</b>", table_cell_bold), Paragraph("संख्यावाच्यव्ययम्", table_cell_style), Paragraph("Numerical / quantifier indeclinable", table_cell_style), Paragraph("सकृत्, त्रिः, बहुशः", table_cell_style)],
        [Paragraph("<b>DVI</b>", table_cell_bold), Paragraph("द्विरुक्तम्", table_cell_style), Paragraph("Reduplicated form for frequency/intensity", table_cell_style), Paragraph("शनैः शनैः, पुनः पुनः", table_cell_style)],
        [Paragraph("<b>A</b>", table_cell_bold), Paragraph("विशेषणम्", table_cell_style), Paragraph("Descriptive qualifying adjective", table_cell_style), Paragraph("नूतनम्, प्राचीनतमा, समृद्धा", table_cell_style)]
    ]

    t_tags = Table(tag_rows, colWidths=[0.6*inch, 1.8*inch, 2.7*inch, 1.9*inch])
    t_tags.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_tags)
    story.append(Spacer(1, 10))

    # Notes section
    story.append(Paragraph("6. Scholar Remarks / Notes", h1_style))
    notes_desc = (
        "At the bottom of each sentence, you may enter optional linguistic remarks in the text area. "
        "Use this for noting compound segmentations (<i>samāsa-vigraha</i>), sandhi ambiguities, or dialectal nuances. "
        "These remarks will be permanently preserved in the exported dissertation dataset."
    )
    story.append(Paragraph(notes_desc, body_style))

    doc.build(story)
    print(f"PDF generated successfully at: {output_filename}")

if __name__ == "__main__":
    generate_pdf()
