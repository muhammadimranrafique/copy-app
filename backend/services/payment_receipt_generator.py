from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import qrcode
import io
from datetime import datetime
from typing import Dict, Any
from config import get_settings
import os

settings = get_settings()




class ProfessionalInvoiceGenerator:
    """Professional A4 single-page invoice generator with eye-catching design."""
    
    def __init__(self):
        self.invoice_dir = settings.invoice_dir
        os.makedirs(self.invoice_dir, exist_ok=True)
        
        # Premium color palette
        self.primary_dark = colors.HexColor('#1e40af')
        self.primary = colors.HexColor('#3b82f6')
        self.primary_light = colors.HexColor('#60a5fa')
        self.success = colors.HexColor('#10b981')
        self.success_light = colors.HexColor('#34d399')
        self.warning = colors.HexColor('#f59e0b')
        self.accent = colors.HexColor('#8b5cf6')
        self.bg_light = colors.HexColor('#f8fafc')
        self.bg_blue = colors.HexColor('#eff6ff')
        self.text_dark = colors.HexColor('#1e293b')
        self.text_medium = colors.HexColor('#475569')
        self.text_light = colors.HexColor('#64748b')
        self.border = colors.HexColor('#cbd5e1')
    
    def _create_premium_header(self, story, styles, receipt_number: str, payment_data: Dict[str, Any]):
        """Create professional header with full width utilization."""
        
        header_content = [
            [
                Paragraph(
                    f'<b><font size=24 color=#1e40af>{settings.company_name}</font></b><br/>'
                    f'<font size=10 color=#64748b>Professional Manufacturing Solutions</font>',
                    ParagraphStyle('CompanyInfo', parent=styles['Normal'], leading=18)
                ),
                Paragraph(
                    f'<b><font size=14 color=white>PAYMENT RECEIPT</font></b><br/>'
                    f'<font size=16 color=white><b>#{receipt_number}</b></font>',
                    ParagraphStyle('ReceiptBadge', parent=styles['Normal'], alignment=TA_CENTER, leading=18)
                )
            ]
        ]
        
        header_table = Table(header_content, colWidths=[120*mm, 75*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (1, 0), (1, 0), self.primary),
            ('TOPPADDING', (1, 0), (1, 0), 12),
            ('BOTTOMPADDING', (1, 0), (1, 0), 12),
            ('LEFTPADDING', (1, 0), (1, 0), 15),
            ('RIGHTPADDING', (1, 0), (1, 0), 15),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ('BOX', (1, 0), (1, 0), 3, self.primary_dark),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
    
    def _create_info_section(self, story, styles, payment_data: Dict[str, Any], client_data: Dict[str, Any]):
        """Create comprehensive information section with modern layout."""
        
        payment_date = payment_data.get('payment_date', datetime.now())
        status = payment_data.get('status', 'COMPLETED')
        
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()
        
        formatted_date = payment_date.strftime('%d %B %Y')
        formatted_time = payment_date.strftime('%I:%M %p')
        
        # Status styling
        status_colors = {
            'COMPLETED': self.success,
            'PENDING': self.warning,
            'PARTIAL': self.primary,
        }
        status_color = status_colors.get(status, colors.grey)
        
        # Create two-column layout
        left_section = [
            [Paragraph('<b><font size=11 color=#1e40af>RECEIVED FROM</font></b>', 
                      ParagraphStyle('SH', parent=styles['Normal'], spaceAfter=3))],
            [Paragraph(f'<b><font size=12>{client_data.get("name", "N/A")}</font></b>', styles['Normal'])],
            [Paragraph(f'<font size=9 color=#64748b><b>Type:</b> {client_data.get("type", "N/A")}</font>', styles['Normal'])],
            [Paragraph(f'<font size=9 color=#64748b><b>Contact:</b> {client_data.get("contact", "N/A")}</font>', styles['Normal'])],
            [Paragraph(f'<font size=9 color=#64748b><b>Address:</b> {client_data.get("address", "N/A")}</font>', styles['Normal'])],
        ]
        
        left_table = Table(left_section, colWidths=[90*mm])
        left_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_blue),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 1.5, self.border),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.primary),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        
        right_section = [
            [Paragraph('<b><font size=11 color=#1e40af>PAYMENT DETAILS</font></b>', 
                      ParagraphStyle('SH', parent=styles['Normal'], spaceAfter=3))],
            [Paragraph(f'<b>Date:</b> {formatted_date}', styles['Normal'])],
            [Paragraph(f'<b>Time:</b> {formatted_time}', styles['Normal'])],
            [Paragraph(f'<b>Method:</b> {payment_data.get("method", "N/A")}', styles['Normal'])],
            [Paragraph(f'<b>Status:</b> <font color={status_color.hexval()}><b>{status}</b></font>', styles['Normal'])],
        ]
        
        if payment_data.get('reference_number'):
            right_section.append([Paragraph(
                f'<font size=8 color=#64748b><b>Ref:</b> {payment_data.get("reference_number")}</font>', 
                styles['Normal']
            )])
        
        right_table = Table(right_section, colWidths=[95*mm])
        right_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_blue),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOX', (0, 0), (-1, -1), 1.5, self.border),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.primary),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        
        # Combine both sections with full width utilization
        combined_data = [[left_table, right_table]]
        combined_table = Table(combined_data, colWidths=[95*mm, 100*mm], hAlign='LEFT')
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(combined_table)
        story.append(Spacer(1, 6*mm))
    
    def _create_amount_spotlight(self, story, styles, payment_data: Dict[str, Any]):
        """Create prominent amount display with professional styling."""
        amount = payment_data.get('amount', 0)
        
        amount_content = [
            [Paragraph('<font size=14 color=#1e40af><b>TOTAL AMOUNT RECEIVED</b></font>', 
                      ParagraphStyle('AL', parent=styles['Normal'], alignment=TA_CENTER))],
            [Paragraph(f'<b><font size=48 color=#10b981>Rs. {amount:,.2f}</font></b>', 
                      ParagraphStyle('AV', parent=styles['Normal'], alignment=TA_CENTER))],
            [Paragraph('<font size=10 color=#64748b>Payment Successfully Processed & Confirmed</font>', 
                      ParagraphStyle('AS', parent=styles['Normal'], alignment=TA_CENTER))],
        ]
        
        amount_table = Table(amount_content, colWidths=[195*mm])
        amount_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (0, 0), 15),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8),
            ('TOPPADDING', (0, 1), (0, 1), 8),
            ('BOTTOMPADDING', (0, 1), (0, 1), 8),
            ('TOPPADDING', (0, 2), (0, 2), 5),
            ('BOTTOMPADDING', (0, 2), (0, 2), 15),
            ('BOX', (0, 0), (-1, -1), 3, self.success),
            ('ROUNDEDCORNERS', [12, 12, 12, 12]),
        ]))
        
        story.append(amount_table)
        story.append(Spacer(1, 6*mm))
    
    def _create_qr_and_thankyou(self, story, styles, payment_data: Dict[str, Any]):
        """Create QR code with elegant thank you message."""
        try:
            # Generate QR code
            receipt_number = payment_data.get('receipt_number', '')
            amount = payment_data.get('amount', 0)
            payment_id = payment_data.get('payment_id', '')

            qr_data = f"RECEIPT:{receipt_number}|ID:{payment_id}|AMT:Rs.{amount:,.2f}|VERIFY:https://verify.receipt/{payment_id}"
            qr = qrcode.QRCode(version=1, box_size=4, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            qr_img = Image(img_buffer, width=50*mm, height=50*mm)

            content_data = [
                [
                    qr_img,
                    Paragraph(
                        '<b><font size=12 color=#1e40af>Thank You for Your Payment!</font></b><br/>'
                        '<font size=8 color=#475569>Payment successfully received and processed. '
                        'Scan QR code to verify receipt online or contact support for assistance.</font><br/>'
                        '<font size=7 color=#64748b><i>Please retain this receipt for your records.</i></font>',
                        ParagraphStyle('TY', parent=styles['Normal'], alignment=TA_LEFT, leading=10)
                    )
                ]
            ]

            content_table = Table(content_data, colWidths=[60*mm, 135*mm])
            content_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (1, 0), (1, 0), 10),
                ('RIGHTPADDING', (1, 0), (1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), self.bg_light),
                ('BOX', (0, 0), (-1, -1), 1, self.border),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
            ]))

            story.append(content_table)

        except Exception as e:
            print(f"Error generating QR code: {e}")
            story.append(Paragraph(
                '<b><font size=12 color=#1e40af>Thank You for Your Payment!</font></b>',
                ParagraphStyle('TY', parent=styles['Normal'], alignment=TA_CENTER)
            ))
    
    def _create_inline_footer(self, story, styles):
        """Create professional inline footer section."""
        story.append(Spacer(1, 10*mm))
        
        # Professional footer with enhanced design
        footer_content = [
            [Paragraph(
                f'<b><font size=12 color=#1e40af>{settings.company_name}</font></b>',
                ParagraphStyle('CompanyName', parent=styles['Normal'], alignment=TA_CENTER)
            )],
            [Paragraph(
                '<font size=9 color=#475569>Professional Manufacturing Solutions & Business Management</font>',
                ParagraphStyle('Tagline', parent=styles['Normal'], alignment=TA_CENTER)
            )],
            [Paragraph(
                f'<font size=8 color=#64748b>📞 {settings.company_phone} | ✉️ {settings.company_email} | 🏭 Manufacturing District</font>',
                ParagraphStyle('Contact', parent=styles['Normal'], alignment=TA_CENTER)
            )],
            [Paragraph(
                '<font size=7 color=#64748b><i>This is a computer-generated receipt. Thank you for your business and trust in our services.</i></font>',
                ParagraphStyle('Disclaimer', parent=styles['Normal'], alignment=TA_CENTER)
            )]
        ]
        
        footer_table = Table(footer_content, colWidths=[195*mm])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 4),
            ('TOPPADDING', (0, 1), (0, 1), 3),
            ('BOTTOMPADDING', (0, 1), (0, 1), 4),
            ('TOPPADDING', (0, 2), (0, 2), 4),
            ('BOTTOMPADDING', (0, 2), (0, 2), 4),
            ('TOPPADDING', (0, 3), (0, 3), 4),
            ('BOTTOMPADDING', (0, 3), (0, 3), 8),
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.primary),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))
        
        story.append(footer_table)

    def generate_receipt(
        self,
        payment_data: Dict[str, Any],
        client_data: Dict[str, Any]
    ) -> str:
        """
        Generate a professional A4 single-page payment receipt PDF.

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

        # Create PDF with optimized A4 margins for maximum content area
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=12*mm,
            leftMargin=12*mm,
            topMargin=8*mm,
            bottomMargin=12*mm,
        )

        story = []
        styles = getSampleStyleSheet()

        # Build premium single-page receipt
        self._create_premium_header(story, styles, receipt_number, payment_data)
        self._create_info_section(story, styles, payment_data, client_data)
        self._create_amount_spotlight(story, styles, payment_data)
        self._create_qr_and_thankyou(story, styles, payment_data)
        self._create_inline_footer(story, styles)

        # Build PDF
        doc.build(story)

        return filepath


# Global instance
payment_receipt_generator = ProfessionalInvoiceGenerator()