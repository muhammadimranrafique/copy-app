
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import qrcode
import io
from datetime import datetime
from typing import Dict, Any
from config import get_settings
import os

settings = get_settings()

class SinglePageCanvas(canvas.Canvas):
    """Custom canvas for single-page invoice with elegant footer."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)

    def save(self):
        """Add elegant footer to the page."""
        self.draw_elegant_footer()
        canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_elegant_footer(self):
        """Draw elegant footer with gradient-like effect."""
        # Footer background bar
        self.setFillColor(colors.HexColor('#1e40af'))
        self.rect(0, 0, A4[0], 0.6*inch, fill=True, stroke=False)
        
        # Company info in white
        self.setFont("Helvetica-Bold", 9)
        self.setFillColor(colors.white)
        footer_text = f"{settings.company_name}"
        self.drawCentredString(A4[0] / 2, 0.38*inch, footer_text)
        
        # Contact details
        self.setFont("Helvetica", 7)
        contact_text = f"{settings.company_phone} • {settings.company_email}"
        self.drawCentredString(A4[0] / 2, 0.22*inch, contact_text)
        
        # Terms text
        self.setFont("Helvetica-Oblique", 6)
        self.setFillColor(colors.HexColor('#93c5fd'))
        terms_text = "This is a computer-generated receipt and does not require a signature"
        self.drawCentredString(A4[0] / 2, 0.1*inch, terms_text)


class ProfessionalInvoiceGenerator:
    """Professional single-page invoice generator with modern design."""
    
    def __init__(self):
        self.invoice_dir = settings.invoice_dir
        os.makedirs(self.invoice_dir, exist_ok=True)
        # Color scheme
        self.primary_color = colors.HexColor('#1e40af')  # Deep blue
        self.secondary_color = colors.HexColor('#3b82f6')  # Bright blue
        self.success_color = colors.HexColor('#10b981')  # Green
        self.light_bg = colors.HexColor('#eff6ff')  # Very light blue
        self.text_dark = colors.HexColor('#1e293b')
        self.text_light = colors.HexColor('#64748b')
    
    def _create_compact_header(self, story, styles, receipt_number: str, payment_data: Dict[str, Any]):
        """Create compact professional header with company branding and receipt info."""
        # Top section with company name and receipt badge
        header_data = [
            [
                Paragraph(f"<b>{settings.company_name}</b>", ParagraphStyle(
                    'CompanyName',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=self.primary_color,
                    fontName='Helvetica-Bold'
                )),
                Paragraph(f"<b>RECEIPT</b><br/><font size=10>#{receipt_number}</font>", ParagraphStyle(
                    'ReceiptBadge',
                    parent=styles['Normal'],
                    fontSize=16,
                    textColor=colors.white,
                    alignment=TA_RIGHT,
                    fontName='Helvetica-Bold'
                ))
            ]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (1, 0), (1, 0), self.primary_color),
            ('TOPPADDING', (1, 0), (1, 0), 8),
            ('BOTTOMPADDING', (1, 0), (1, 0), 8),
            ('LEFTPADDING', (1, 0), (1, 0), 12),
            ('RIGHTPADDING', (1, 0), (1, 0), 12),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 0.15*inch))
        
        # Tagline
        tagline_style = ParagraphStyle(
            'Tagline',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.text_light,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique'
        )
        story.append(Paragraph("Manufacturing Business Management System", tagline_style))
        story.append(Spacer(1, 0.2*inch))
    
    def _create_info_grid(self, story, styles, payment_data: Dict[str, Any], client_data: Dict[str, Any]):
        """Create compact info grid with payment and client details."""
        payment_date = payment_data.get('payment_date', datetime.now())
        status = payment_data.get('status', 'COMPLETED')
        
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()
        
        formatted_date = payment_date.strftime('%b %d, %Y')
        formatted_time = payment_date.strftime('%I:%M %p')
        
        # Status badge
        status_colors = {
            'COMPLETED': self.success_color,
            'PENDING': colors.HexColor('#f59e0b'),
            'PARTIAL': self.secondary_color,
        }
        status_color = status_colors.get(status, colors.grey)
        
        # Left and right info sections side by side
        info_data = [
            [
                Paragraph('<b>RECEIVED FROM</b>', ParagraphStyle(
                    'SectionHead', parent=styles['Normal'], fontSize=10,
                    textColor=self.primary_color, fontName='Helvetica-Bold'
                )),
                Paragraph('<b>PAYMENT INFO</b>', ParagraphStyle(
                    'SectionHead', parent=styles['Normal'], fontSize=10,
                    textColor=self.primary_color, fontName='Helvetica-Bold'
                ))
            ],
            [
                Paragraph(f"<b>{client_data.get('name', 'N/A')}</b><br/>"
                         f"<font size=8>{client_data.get('type', 'N/A')}</font>", 
                         styles['Normal']),
                Paragraph(f"<b>Date:</b> {formatted_date} at {formatted_time}", styles['Normal'])
            ],
            [
                Paragraph(f"<font size=8>{client_data.get('contact', 'N/A')}</font>", styles['Normal']),
                Paragraph(f"<b>Method:</b> {payment_data.get('method', 'N/A')}", styles['Normal'])
            ],
            [
                Paragraph(f"<font size=8>{client_data.get('address', 'N/A')}</font>", styles['Normal']),
                Paragraph(f"<b>Status:</b> <font color={status_color.hexval()}><b>{status}</b></font>", styles['Normal'])
            ],
        ]
        
        info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.light_bg),
            ('BACKGROUND', (1, 0), (1, 0), self.light_bg),
            ('SPAN', (0, 0), (0, 0)),
            ('SPAN', (1, 0), (1, 0)),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.primary_color),
            ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.25*inch))
    
    def _create_amount_showcase(self, story, styles, payment_data: Dict[str, Any]):
        """Create eye-catching amount display with payment details."""
        amount = payment_data.get('amount', 0)
        reference = payment_data.get('reference_number', '')
        
        # Main amount display
        amount_data = [
            [
                Paragraph('<font size=11 color=#64748b>TOTAL AMOUNT RECEIVED</font>', 
                         ParagraphStyle('AmtLabel', parent=styles['Normal'], alignment=TA_CENTER))
            ],
            [
                Paragraph(f'<b><font size=36 color=#10b981>Rs. {amount:,.2f}</font></b>', 
                         ParagraphStyle('AmtValue', parent=styles['Normal'], alignment=TA_CENTER))
            ],
        ]
        
        if reference:
            amount_data.append([
                Paragraph(f'<font size=8 color=#64748b>Reference: <b>{reference}</b></font>', 
                         ParagraphStyle('RefLabel', parent=styles['Normal'], alignment=TA_CENTER))
            ])
        
        amount_table = Table(amount_data, colWidths=[7*inch])
        amount_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 1), (-1, 1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, self.success_color),
            ('ROUNDEDCORNERS', [12, 12, 12, 12]),
        ]))
        
        story.append(amount_table)
        story.append(Spacer(1, 0.25*inch))
    
    def _create_qr_and_footer(self, story, styles, payment_data: Dict[str, Any]):
        """Create compact QR code and thank you section."""
        try:
            # Generate QR code
            receipt_number = payment_data.get('receipt_number', '')
            amount = payment_data.get('amount', 0)
            payment_id = payment_data.get('payment_id', '')

            qr_data = f"Receipt:{receipt_number}|ID:{payment_id}|Amount:Rs.{amount:,.2f}"
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            qr_img = Image(img_buffer, width=80, height=80)

            # QR code with thank you message side by side
            footer_data = [
                [
                    qr_img,
                    Paragraph(
                        '<b><font size=13 color=#1e40af>Thank You for Your Payment!</font></b><br/><br/>'
                        '<font size=8 color=#64748b>This receipt confirms your payment has been received. '
                        'Please scan the QR code for verification or keep this receipt for your records.</font>',
                        ParagraphStyle('ThankYou', parent=styles['Normal'], alignment=TA_LEFT)
                    )
                ]
            ]

            footer_table = Table(footer_data, colWidths=[1.2*inch, 5.8*inch])
            footer_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (1, 0), (1, 0), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ]))

            story.append(footer_table)

        except Exception as e:
            print(f"Error generating QR code: {e}")
            # Fallback without QR
            story.append(Paragraph(
                '<b><font size=13 color=#1e40af>Thank You for Your Payment!</font></b>',
                ParagraphStyle('ThankYou', parent=styles['Normal'], alignment=TA_CENTER)
            ))

    def generate_receipt(
        self,
        payment_data: Dict[str, Any],
        client_data: Dict[str, Any]
    ) -> str:
        """
        Generate a professional single-page payment receipt PDF.

        Args:
            payment_data: Dictionary containing payment information
                - payment_id: UUID of the payment
                - amount: Payment amount
                - method: Payment method (Cash, Bank Transfer, etc.)
                - status: Payment status
                - payment_date: Date of payment
                - reference_number: Optional reference number
            client_data: Dictionary containing client/leader information
                - name: Client name
                - type: Client type (School/Dealer)
                - contact: Contact information
                - address: Client address

        Returns:
            str: Path to the generated PDF file
        """
        payment_id = payment_data.get('payment_id', '')
        payment_date = payment_data.get('payment_date', datetime.now())
        reference_number = payment_data.get('reference_number', '')

        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()

        date_str = payment_date.strftime('%Y-%m-%d')
        receipt_number = f"RCPT-{str(payment_id)[:8].upper()}"
        payment_data['receipt_number'] = receipt_number

        filename = f"receipt_{reference_number}_{date_str}.pdf" if reference_number else f"receipt_{str(payment_id)[:8]}_{date_str}.pdf"
        filepath = os.path.join(self.invoice_dir, filename)

        # Create PDF with optimized margins for single page
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.5*inch,
            bottomMargin=0.8*inch,
        )

        story = []
        styles = getSampleStyleSheet()

        # Build compact single-page receipt
        self._create_compact_header(story, styles, receipt_number, payment_data)
        self._create_info_grid(story, styles, payment_data, client_data)
        self._create_amount_showcase(story, styles, payment_data)
        self._create_qr_and_footer(story, styles, payment_data)

        # Build PDF with custom canvas
        doc.build(story, canvasmaker=SinglePageCanvas)

        return filepath


# Global instance
payment_receipt_generator = ProfessionalInvoiceGenerator()

# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# from reportlab.pdfgen import canvas
# import qrcode
# import io
# from datetime import datetime
# from typing import Dict, Any, Optional
# from config import get_settings
# import os

# settings = get_settings()

# class NumberedCanvas(canvas.Canvas):
#     """Custom canvas to add page numbers and footer to each page."""
    
#     def __init__(self, *args, **kwargs):
#         canvas.Canvas.__init__(self, *args, **kwargs)
#         self._saved_page_states = []

#     def showPage(self):
#         self._saved_page_states.append(dict(self.__dict__))
#         self._startPage()

#     def save(self):
#         """Add page numbers and footer to each page."""
#         num_pages = len(self._saved_page_states)
#         for state in self._saved_page_states:
#             self.__dict__.update(state)
#             self.draw_page_number(num_pages)
#             self.draw_footer()
#             canvas.Canvas.showPage(self)
#         canvas.Canvas.save(self)

#     def draw_page_number(self, page_count):
#         """Draw page number at bottom right."""
#         self.setFont("Helvetica", 9)
#         self.setFillColor(colors.grey)
#         self.drawRightString(
#             A4[0] - 0.75*inch,
#             0.5*inch,
#             f"Page {self._pageNumber} of {page_count}"
#         )

#     def draw_footer(self):
#         """Draw footer with company info and terms."""
#         self.setFont("Helvetica", 8)
#         self.setFillColor(colors.HexColor('#666666'))
        
#         # Company info
#         footer_text = f"{settings.company_name} | {settings.company_phone} | {settings.company_email}"
#         self.drawCentredString(A4[0] / 2, 0.75*inch, footer_text)
        
#         # Terms
#         terms_text = "This is a computer-generated receipt and does not require a signature."
#         self.setFont("Helvetica-Oblique", 7)
#         self.setFillColor(colors.grey)
#         self.drawCentredString(A4[0] / 2, 0.5*inch, terms_text)


# class PaymentReceiptGenerator:
#     """Professional payment receipt/invoice generator with eye-catching design."""
    
#     def __init__(self):
#         self.invoice_dir = settings.invoice_dir
#         os.makedirs(self.invoice_dir, exist_ok=True)
    
#     def _create_header(self, story, styles, receipt_number: str):
#         """Create professional header with company branding."""
#         # Company Name - Eye-catching title
#         title_style = ParagraphStyle(
#             'CompanyTitle',
#             parent=styles['Heading1'],
#             fontSize=28,
#             textColor=colors.HexColor('#1e40af'),
#             spaceAfter=5,
#             alignment=TA_CENTER,
#             fontName='Helvetica-Bold'
#         )
        
#         subtitle_style = ParagraphStyle(
#             'CompanySubtitle',
#             parent=styles['Normal'],
#             fontSize=12,
#             textColor=colors.HexColor('#64748b'),
#             spaceAfter=20,
#             alignment=TA_CENTER,
#             fontName='Helvetica-Oblique'
#         )
        
#         # Header with company name
#         story.append(Paragraph(f"<b>{settings.company_name}</b>", title_style))
#         story.append(Paragraph("Manufacturing Business Management", subtitle_style))
        
#         # Horizontal line separator
#         line_data = [['', '']]
#         line_table = Table(line_data, colWidths=[7*inch])
#         line_table.setStyle(TableStyle([
#             ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor('#1e40af')),
#             ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#94a3b8')),
#         ]))
#         story.append(line_table)
#         story.append(Spacer(1, 0.3*inch))
        
#         # Receipt title banner
#         receipt_title_style = ParagraphStyle(
#             'ReceiptTitle',
#             parent=styles['Heading2'],
#             fontSize=20,
#             textColor=colors.whitesmoke,
#             alignment=TA_CENTER,
#             fontName='Helvetica-Bold'
#         )
        
#         receipt_banner_data = [[Paragraph('PAYMENT RECEIPT', receipt_title_style)]]
#         receipt_banner = Table(receipt_banner_data, colWidths=[7*inch])
#         receipt_banner.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 15),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
#             ('ROUNDEDCORNERS', [10, 10, 10, 10]),
#         ]))
#         story.append(receipt_banner)
#         story.append(Spacer(1, 0.4*inch))
    
#     def _create_receipt_info_section(self, story, styles, payment_data: Dict[str, Any]):
#         """Create receipt information section."""
#         receipt_number = payment_data.get('receipt_number', '')
#         payment_date = payment_data.get('payment_date', datetime.now())
#         status = payment_data.get('status', 'COMPLETED')
        
#         # Format date
#         if isinstance(payment_date, str):
#             try:
#                 payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
#             except:
#                 payment_date = datetime.now()
        
#         formatted_date = payment_date.strftime('%B %d, %Y')
#         formatted_time = payment_date.strftime('%I:%M %p')
        
#         # Status badge color
#         status_colors = {
#             'COMPLETED': colors.HexColor('#10b981'),
#             'PENDING': colors.HexColor('#f59e0b'),
#             'PARTIAL': colors.HexColor('#3b82f6'),
#         }
#         status_color = status_colors.get(status, colors.grey)
        
#         # Receipt info table
#         info_data = [
#             ['Receipt Number:', receipt_number, 'Status:', status],
#             ['Payment Date:', formatted_date, 'Time:', formatted_time],
#         ]
        
#         info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2.5*inch])
#         info_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
#             ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f1f5f9')),
#             ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#334155')),
#             ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#334155')),
#             ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#             ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
#             ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
#             ('ALIGN', (1, 0), (1, -1), 'LEFT'),
#             ('ALIGN', (3, 0), (3, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
#             ('LEFTPADDING', (0, 0), (-1, -1), 10),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 10),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
#             # Status badge styling
#             ('BACKGROUND', (3, 0), (3, 0), status_color),
#             ('TEXTCOLOR', (3, 0), (3, 0), colors.whitesmoke),
#             ('FONTNAME', (3, 0), (3, 0), 'Helvetica-Bold'),
#             ('ALIGN', (3, 0), (3, 0), 'CENTER'),
#         ]))
        
#         story.append(info_table)
#         story.append(Spacer(1, 0.4*inch))
    
#     def _create_client_section(self, story, styles, client_data: Dict[str, Any]):
#         """Create client/leader information section."""
#         section_title_style = ParagraphStyle(
#             'SectionTitle',
#             parent=styles['Heading3'],
#             fontSize=14,
#             textColor=colors.HexColor('#1e40af'),
#             spaceAfter=10,
#             fontName='Helvetica-Bold'
#         )
        
#         story.append(Paragraph('RECEIVED FROM', section_title_style))
        
#         client_info_data = [
#             ['Name:', client_data.get('name', 'N/A')],
#             ['Type:', client_data.get('type', 'N/A')],
#             ['Contact:', client_data.get('contact', 'N/A')],
#             ['Address:', client_data.get('address', 'N/A')],
#         ]
        
#         client_table = Table(client_info_data, colWidths=[1.5*inch, 5.5*inch])
#         client_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
#             ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
#             ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
#             ('ALIGN', (1, 0), (1, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
#             ('LEFTPADDING', (0, 0), (-1, -1), 10),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 10),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
#         ]))
        
#         story.append(client_table)
#         story.append(Spacer(1, 0.4*inch))
    
#     def _create_payment_details_section(self, story, styles, payment_data: Dict[str, Any]):
#         """Create payment details section with amount and method."""
#         section_title_style = ParagraphStyle(
#             'SectionTitle',
#             parent=styles['Heading3'],
#             fontSize=14,
#             textColor=colors.HexColor('#1e40af'),
#             spaceAfter=10,
#             fontName='Helvetica-Bold'
#         )
        
#         story.append(Paragraph('PAYMENT DETAILS', section_title_style))
        
#         amount = payment_data.get('amount', 0)
#         method = payment_data.get('method', 'N/A')
#         reference = payment_data.get('reference_number', 'N/A')
        
#         # Payment details table
#         details_data = [
#             ['Description', 'Details'],
#             ['Payment Method', method],
#             ['Reference Number', reference if reference else 'N/A'],
#         ]
        
#         details_table = Table(details_data, colWidths=[2.5*inch, 4.5*inch])
#         details_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, 0), 12),
#             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
#             ('FONTSIZE', (0, 1), (-1, -1), 10),
#             ('ALIGN', (0, 1), (0, -1), 'LEFT'),
#             ('ALIGN', (1, 1), (1, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 10),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
#             ('LEFTPADDING', (0, 0), (-1, -1), 12),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 12),
#             ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
#         ]))
        
#         story.append(details_table)
#         story.append(Spacer(1, 0.4*inch))
        
#         # Amount section - Eye-catching
#         amount_title_style = ParagraphStyle(
#             'AmountTitle',
#             parent=styles['Normal'],
#             fontSize=12,
#             textColor=colors.HexColor('#64748b'),
#             alignment=TA_CENTER,
#             spaceAfter=5,
#         )
        
#         amount_value_style = ParagraphStyle(
#             'AmountValue',
#             parent=styles['Heading1'],
#             fontSize=32,
#             textColor=colors.HexColor('#10b981'),
#             alignment=TA_CENTER,
#             fontName='Helvetica-Bold',
#             spaceAfter=10,
#         )
        
#         amount_box_data = [
#             [Paragraph('AMOUNT RECEIVED', amount_title_style)],
#             [Paragraph(f'Rs. {amount:,.2f}', amount_value_style)],
#         ]
        
#         amount_box = Table(amount_box_data, colWidths=[7*inch])
#         amount_box.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 20),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
#             ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#10b981')),
#             ('ROUNDEDCORNERS', [10, 10, 10, 10]),
#         ]))
        
#         story.append(amount_box)
#         story.append(Spacer(1, 0.5*inch))

#     def _create_qr_code_section(self, story, styles, payment_data: Dict[str, Any]):
#         """Create QR code for verification."""
#         try:
#             receipt_number = payment_data.get('receipt_number', '')
#             amount = payment_data.get('amount', 0)
#             payment_id = payment_data.get('payment_id', '')

#             qr_data = f"Receipt: {receipt_number}\nPayment ID: {payment_id}\nAmount: Rs. {amount:,.2f}"
#             qr = qrcode.QRCode(version=1, box_size=4, border=2)
#             qr.add_data(qr_data)
#             qr.make(fit=True)

#             img = qr.make_image(fill_color='black', back_color='white')
#             img_buffer = io.BytesIO()
#             img.save(img_buffer, format='PNG')
#             img_buffer.seek(0)

#             qr_img = Image(img_buffer, width=120, height=120)

#             qr_title_style = ParagraphStyle(
#                 'QRTitle',
#                 parent=styles['Normal'],
#                 fontSize=10,
#                 textColor=colors.HexColor('#64748b'),
#                 alignment=TA_CENTER,
#                 spaceAfter=10,
#             )

#             story.append(Paragraph('<b>Scan for Verification</b>', qr_title_style))

#             # Center the QR code
#             qr_table = Table([[qr_img]], colWidths=[7*inch])
#             qr_table.setStyle(TableStyle([
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ]))
#             story.append(qr_table)

#         except Exception as e:
#             print(f"Error generating QR code: {e}")

#         story.append(Spacer(1, 0.3*inch))

#     def _create_thank_you_section(self, story, styles):
#         """Create thank you message."""
#         thank_you_style = ParagraphStyle(
#             'ThankYou',
#             parent=styles['Normal'],
#             fontSize=12,
#             textColor=colors.HexColor('#1e40af'),
#             alignment=TA_CENTER,
#             fontName='Helvetica-BoldOblique',
#         )

#         story.append(Paragraph('Thank you for your payment!', thank_you_style))
#         story.append(Spacer(1, 0.2*inch))

#         note_style = ParagraphStyle(
#             'Note',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=colors.HexColor('#64748b'),
#             alignment=TA_CENTER,
#             fontName='Helvetica-Oblique',
#         )

#         story.append(Paragraph(
#             'For any queries regarding this receipt, please contact us at the details provided below.',
#             note_style
#         ))

#     def generate_receipt(
#         self,
#         payment_data: Dict[str, Any],
#         client_data: Dict[str, Any]
#     ) -> str:
#         """
#         Generate a professional payment receipt PDF.

#         Args:
#             payment_data: Dictionary containing payment information
#                 - payment_id: UUID of the payment
#                 - amount: Payment amount
#                 - method: Payment method (Cash, Bank Transfer, etc.)
#                 - status: Payment status
#                 - payment_date: Date of payment
#                 - reference_number: Optional reference number
#             client_data: Dictionary containing client/leader information
#                 - name: Client name
#                 - type: Client type (School/Dealer)
#                 - contact: Contact information
#                 - address: Client address

#         Returns:
#             str: Path to the generated PDF file
#         """
#         payment_id = payment_data.get('payment_id', '')
#         payment_date = payment_data.get('payment_date', datetime.now())
#         reference_number = payment_data.get('reference_number', '')

#         # Format date for filename
#         if isinstance(payment_date, str):
#             try:
#                 payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
#             except:
#                 payment_date = datetime.now()

#         date_str = payment_date.strftime('%Y-%m-%d')

#         # Generate receipt number
#         receipt_number = f"RCPT-{str(payment_id)[:8].upper()}"
#         payment_data['receipt_number'] = receipt_number

#         # Create filename
#         if reference_number:
#             filename = f"payment_receipt_{reference_number}_{date_str}.pdf"
#         else:
#             filename = f"payment_receipt_{str(payment_id)[:8]}_{date_str}.pdf"

#         filepath = os.path.join(self.invoice_dir, filename)

#         # Create PDF document with custom canvas for page numbers and footer
#         doc = SimpleDocTemplate(
#             filepath,
#             pagesize=A4,
#             rightMargin=0.75*inch,
#             leftMargin=0.75*inch,
#             topMargin=0.75*inch,
#             bottomMargin=1.25*inch,  # Extra space for footer
#         )

#         story = []
#         styles = getSampleStyleSheet()

#         # Build the receipt
#         self._create_header(story, styles, receipt_number)
#         self._create_receipt_info_section(story, styles, payment_data)
#         self._create_client_section(story, styles, client_data)
#         self._create_payment_details_section(story, styles, payment_data)
#         self._create_qr_code_section(story, styles, payment_data)
#         self._create_thank_you_section(story, styles)

#         # Build PDF with custom canvas
#         doc.build(story, canvasmaker=NumberedCanvas)

#         return filepath


# # Global instance
# payment_receipt_generator = PaymentReceiptGenerator()

