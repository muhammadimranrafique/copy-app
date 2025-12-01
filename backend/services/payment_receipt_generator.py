from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
import io
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import get_settings
import os

settings = get_settings()

class PaymentReceiptGenerator:
    """Professional A4 single-page payment receipt generator."""
    
    def __init__(self):
        # Use a receipts directory sibling to invoices
        self.receipt_dir = os.path.join(os.path.dirname(settings.invoice_dir), "receipts")
        os.makedirs(self.receipt_dir, exist_ok=True)

        # Professional Color Palette
        self.primary_dark = colors.HexColor('#1e40af')      # Dark blue
        self.primary = colors.HexColor('#3b82f6')           # Blue
        self.primary_light = colors.HexColor('#60a5fa')     # Light blue
        self.success = colors.HexColor('#10b981')           # Green
        self.warning = colors.HexColor('#f59e0b')           # Yellow/Gold
        self.danger = colors.HexColor('#ef4444')            # Red
        self.orange = colors.HexColor('#ea580c')            # Orange
        self.bg_light = colors.HexColor('#f8fafc')          # Light gray
        self.bg_blue = colors.HexColor('#eff6ff')           # Light blue bg
        self.bg_green = colors.HexColor('#dcfce7')          # Light green bg
        self.bg_red = colors.HexColor('#fef2f2')            # Light red bg
        self.bg_orange = colors.HexColor('#fff7ed')         # Light orange bg
        self.text_dark = colors.HexColor('#1e293b')         # Dark text
        self.text_medium = colors.HexColor('#475569')       # Medium text
        self.text_light = colors.HexColor('#64748b')        # Light text
        self.border = colors.HexColor('#cbd5e1')            # Border gray

    def _create_header(self, story, styles, receipt_number: str, company_settings: Optional[Dict[str, Any]] = None):
        """Create professional header with Company Name and Receipt Badge."""
        company_name = (company_settings or {}).get('company_name', settings.company_name)
        
        # Left: Company Info
        company_info = Paragraph(
            f'<b><font size=18 color={self.primary_dark}>{company_name}</font></b><br/>'
            f'<font size=9 color={self.text_light}>Professional Manufacturing Solutions</font>',
            ParagraphStyle('CompanyInfo', parent=styles['Normal'], leading=12)
        )

        # Right: Receipt Badge
        receipt_badge_content = [
            [Paragraph(
                f'<b><font size=11 color=white>PAYMENT RECEIPT</font></b><br/>'
                f'<font size=12 color=white><b>#{receipt_number}</b></font>',
                ParagraphStyle('ReceiptBadgeText', parent=styles['Normal'], alignment=TA_CENTER, leading=14)
            )]
        ]
        receipt_badge = Table(receipt_badge_content, colWidths=[60*mm])
        receipt_badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.primary),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))

        # Header Layout Table
        header_data = [[company_info, receipt_badge]]
        header_table = Table(header_data, colWidths=[130*mm, 60*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 5*mm))

    def _create_receipt_details(self, story, styles, order_data: Dict[str, Any], client_data: Dict[str, Any], payment_data: Dict[str, Any]):
        """Create receipt details section."""
        
        # Format dates
        payment_date_str = payment_data.get('payment_date', datetime.now().isoformat())
        try:
            payment_date = datetime.fromisoformat(payment_date_str.replace('Z', '+00:00'))
        except:
            payment_date = datetime.now()
        formatted_date = payment_date.strftime('%d %B %Y')

        # --- Left Card: RECEIVED FROM ---
        received_from_header = Paragraph(
            '<b><font size=10 color=#1e40af>RECEIVED FROM</font></b>',
            ParagraphStyle('CardHeader', parent=styles['Normal'], spaceAfter=0)
        )
        
        received_from_content = [
            [received_from_header],
            [Paragraph(f'<b><font size=11>{client_data.get("name", "N/A")}</font></b>', styles['Normal'])],
            [Paragraph(f'<font size=8 color=#64748b>Contact: {client_data.get("contact", "N/A")}</font>', styles['Normal'])],
        ]
        
        received_from_table = Table(received_from_content, colWidths=[90*mm])
        received_from_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.bg_blue),
            ('TOPPADDING', (0, 0), (0, 0), 6),
            ('BOTTOMPADDING', (0, 0), (0, 0), 6),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('LINEBELOW', (0, 0), (0, 0), 1, self.primary_light),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, self.border),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))

        # --- Right Card: RECEIPT DETAILS ---
        details_header = Paragraph(
            '<b><font size=10 color=#1e40af>RECEIPT DETAILS</font></b>',
            ParagraphStyle('CardHeader', parent=styles['Normal'], spaceAfter=0)
        )
        
        details_content = [
            [details_header],
            [Paragraph(f'<b>Date:</b> {formatted_date}', styles['Normal'])],
            [Paragraph(f'<b>Payment Mode:</b> {payment_data.get("mode", "N/A")}', styles['Normal'])],
            [Paragraph(f'<b>Reference:</b> {payment_data.get("reference_number", "N/A")}', styles['Normal'])],
        ]
        
        details_table = Table(details_content, colWidths=[90*mm])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.bg_blue),
            ('TOPPADDING', (0, 0), (0, 0), 6),
            ('BOTTOMPADDING', (0, 0), (0, 0), 6),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('LINEBELOW', (0, 0), (0, 0), 1, self.primary_light),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, self.border),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))

        # Layout for Cards
        cards_layout = Table([[received_from_table, details_table]], colWidths=[95*mm, 95*mm])
        cards_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        story.append(cards_layout)
        story.append(Spacer(1, 4*mm))

    def _create_amount_spotlight(self, story, styles, payment_data: Dict[str, Any], company_settings: Optional[Dict[str, Any]] = None):
        """Create a prominent spotlight section for the received amount."""
        currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')
        amount = float(payment_data.get('amount', 0))
        
        # Define custom green colors for this section
        green_bg = '#dcfce7'      # Light green background
        green_text = '#10b981'    # Bright green text
        green_border = '#10b981'  # Green border
        
        content = [
            [Paragraph('CURRENT PAYMENT RECEIVED', ParagraphStyle('SpotlightLabel', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, textColor='#374151', spaceAfter=6))],
            [Paragraph(f'<b><font size=48 color={green_text}>{currency_symbol} {amount:,.2f}</font></b>', ParagraphStyle('SpotlightAmount', parent=styles['Normal'], alignment=TA_CENTER, leading=56))],
            [Paragraph(f'<font color={green_text} size=10>✓ Payment Successfully Processed</font>', ParagraphStyle('SpotlightMsg', parent=styles['Normal'], alignment=TA_CENTER, spaceBefore=4))],
        ]
        
        spotlight_table = Table(content, colWidths=[190*mm])
        spotlight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), green_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 3, green_border), # Thick green border
            ('ROUNDEDCORNERS', [12, 12, 12, 12]),       # More rounded corners
        ]))
        
        story.append(spotlight_table)
        story.append(Spacer(1, 8*mm))

    def _create_payment_summary(self, story, styles, order_data: Dict[str, Any], payment_history: List[Dict[str, Any]], company_settings: Optional[Dict[str, Any]] = None):
        """Create comprehensive payment summary table."""
        currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')
        
        # Extract values BEFORE null check (CRITICAL FIX)
        # If order_data is None or empty, these will be 0
        total_amount = float((order_data or {}).get('total_amount', 0))
        
        # Handle None payment_history safely
        safe_history = payment_history or []
        total_paid = sum(float(p.get('amount', 0)) for p in safe_history)
        
        # Defensive check: Handle None order_data
        # This block is now redundant for total_amount calculation, but kept for potential future uses of order_data
        if order_data is None:
            order_data = {}
        
        balance_due = total_amount - total_paid
        
        # Ensure balance isn't negative due to float precision
        if balance_due < 0: balance_due = 0

        # Section Header
        story.append(Paragraph(
            f'<b><font color={self.primary_dark}>💳 PAYMENT BREAKDOWN</font></b>',
            ParagraphStyle('SummaryHeader', parent=styles['Normal'], fontSize=10, spaceAfter=4)
        ))
        story.append(Spacer(1, 2*mm))

        # Headers
        headers = [
            Paragraph('<b>Total Order Amount</b>', ParagraphStyle('H1', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=self.text_medium)),
            Paragraph('<b>Total Paid to Date</b>', ParagraphStyle('H2', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=self.text_medium)),
            Paragraph('<b>Remaining Balance</b>', ParagraphStyle('H3', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=self.text_medium)),
        ]
        
        # Values
        values = [
            Paragraph(f'<b><font size=13 color={self.danger}>{currency_symbol} {total_amount:,.2f}</font></b>', 
                     ParagraphStyle('V1', parent=styles['Normal'], alignment=TA_CENTER)),
            Paragraph(f'<b><font size=13 color={self.primary}>{currency_symbol} {total_paid:,.2f}</font></b>', 
                     ParagraphStyle('V2', parent=styles['Normal'], alignment=TA_CENTER)),
            Paragraph(f'<b><font size=13 color={self.orange}>{currency_symbol} {balance_due:,.2f}</font></b>', 
                     ParagraphStyle('V3', parent=styles['Normal'], alignment=TA_CENTER)),
        ]

        summary_data = [headers, values]
        summary_table = Table(summary_data, colWidths=[63*mm, 63*mm, 64*mm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, self.primary),
            ('BOX', (0, 0), (-1, -1), 1.5, self.primary),
            # Header Row
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_blue),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Value Row
            ('BACKGROUND', (0, 1), (0, 1), self.bg_red),      # Red bg for Total
            ('BACKGROUND', (1, 1), (1, 1), self.bg_blue),     # Blue bg for Paid
            ('BACKGROUND', (2, 1), (2, 1), self.bg_orange),   # Orange bg for Balance
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 5*mm))

    def _create_payment_history(self, story, styles, payment_history: List[Dict[str, Any]], current_payment_id: int, company_settings: Optional[Dict[str, Any]] = None):
        """Create payment history table showing previous payments."""
        currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')
        
        # Handle None payment_history safely
        safe_history = payment_history or []
        
        # Filter out current payment and sort chronologically
        previous_payments = [p for p in safe_history if p.get('id') != current_payment_id]
        previous_payments.sort(key=lambda x: x.get('payment_date', ''))
        
        # Limit to most recent 8 payments
        MAX_DISPLAY_ROWS = 8
        display_note = ""
        if len(previous_payments) > MAX_DISPLAY_ROWS:
            previous_payments = previous_payments[-MAX_DISPLAY_ROWS:]
            display_note = f"(Showing {MAX_DISPLAY_ROWS} most recent payments out of {len(payment_history) - 1} total)"
        
        # Section Header
        header_text = '<b>📋 PREVIOUS PAYMENTS</b>'
        if display_note:
            header_text += f'<br/><font size=7 color=#64748b>{display_note}</font>'
        
        story.append(Paragraph(header_text, ParagraphStyle('HistoryHeader', parent=styles['Normal'], fontSize=10, spaceAfter=4, leading=12)))
        story.append(Spacer(1, 2*mm))

        # If no previous payments
        if not previous_payments:
            msg = Paragraph(
                "✓ This is the first payment for this order",
                ParagraphStyle('NoHistory', parent=styles['Normal'], alignment=TA_CENTER, textColor=self.text_light, fontSize=9)
            )
            story.append(msg)
            story.append(Spacer(1, 4*mm))
            return

        # Table Headers
        table_data = [['Date', 'Reference', 'Mode', 'Amount']]
        
        for p in previous_payments:
            p_date_str = p.get('payment_date', '')
            try:
                p_date = datetime.fromisoformat(p_date_str.replace('Z', '+00:00'))
                formatted_p_date = p_date.strftime('%d-%b-%Y')
            except:
                formatted_p_date = p_date_str[:10]
                
            table_data.append([
                formatted_p_date,
                p.get('reference_number', '-'),
                p.get('mode', '-'),
                f"{currency_symbol} {float(p.get('amount', 0)):,.2f}"
            ])
            
        history_table = Table(table_data, colWidths=[40*mm, 60*mm, 40*mm, 50*mm])
        history_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'), # Align amount right
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Rows
            ('GRID', (0, 0), (-1, -1), 0.5, self.border),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_light]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(history_table)
        story.append(Spacer(1, 5*mm))

    def generate_receipt(self, order_data: Dict[str, Any], client_data: Dict[str, Any], payment_data: Dict[str, Any], payment_history: List[Dict[str, Any]], company_settings: Optional[Dict[str, Any]] = None) -> str:
        """Generate professional payment receipt PDF."""
        receipt_number = f"RCPT-{payment_data.get('id', 'NEW')}"
        receipt_date = datetime.now().strftime('%Y-%m-%d')
        
        filename = f"receipt_{receipt_number}_{receipt_date}.pdf"
        filepath = os.path.join(self.receipt_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=10*mm,
            leftMargin=10*mm,
            topMargin=10*mm,
            bottomMargin=10*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        self._create_header(story, styles, receipt_number, company_settings)
        self._create_receipt_details(story, styles, order_data, client_data, payment_data)
        self._create_amount_spotlight(story, styles, payment_data, company_settings)
        self._create_payment_summary(story, styles, order_data, payment_history, company_settings)
        self._create_payment_history(story, styles, payment_history, payment_data.get('id'), company_settings)
        
        # Footer Section (QR + Thank You + Bottom Bar)
        # QR Code
        qr_img = None
        try:
            amount = payment_data.get('amount', 0)
            qr_data = f"RECEIPT:{receipt_number}|AMT:{amount}"
            qr = qrcode.QRCode(version=1, box_size=3, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            qr_img = Image(img_buffer, width=20*mm, height=20*mm)
        except Exception:
            pass

        # Thank You Message
        thank_you_text = [
            Paragraph('<b>Thank You for Your Payment!</b>', ParagraphStyle('TY1', parent=styles['Normal'], fontSize=8, textColor=self.primary_dark)),
            Paragraph('For any questions regarding this receipt, please contact our support.', ParagraphStyle('TY2', parent=styles['Normal'], fontSize=7, textColor=self.text_light)),
        ]
        
        # Layout: QR Left, Text Right (inside a grey box)
        footer_content = []
        if qr_img:
            footer_content.append([qr_img, thank_you_text])
        else:
            footer_content.append([None, thank_you_text])
            
        footer_table = Table(footer_content, colWidths=[30*mm, 160*mm])
        footer_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), self.bg_light),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(footer_table)
        story.append(Spacer(1, 4*mm))

        # Bottom Bar
        company_name = (company_settings or {}).get('company_name', settings.company_name)
        company_address = (company_settings or {}).get('company_address', settings.company_address)
        
        bottom_bar = Paragraph(
            f'<b>{company_name}</b> | {company_address} | Professional Manufacturing Solutions',
            ParagraphStyle('BottomBar', parent=styles['Normal'], alignment=TA_CENTER, fontSize=7, textColor=self.text_light)
        )
        
        # Add a line before bottom bar
        story.append(Table([['']], colWidths=[190*mm], style=TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, self.primary_light)])))
        story.append(Spacer(1, 2*mm))
        story.append(bottom_bar)
        
        doc.build(story)
        return filepath

# Global instance
payment_receipt_generator = PaymentReceiptGenerator()