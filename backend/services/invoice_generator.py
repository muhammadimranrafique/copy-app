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

class ProfessionalInvoiceGenerator:
    """Professional A4 single-page invoice generator with premium design matching reference image."""
    
    def __init__(self):
        self.invoice_dir = settings.invoice_dir
        os.makedirs(self.invoice_dir, exist_ok=True)

        # Premium color palette (matching reference image)
        self.primary_dark = colors.HexColor('#1e40af')  # Royal Blue
        self.primary = colors.HexColor('#2563eb')       # Bright Blue
        self.primary_light = colors.HexColor('#eff6ff') # Very Light Blue (Backgrounds)
        self.bg_light = colors.HexColor('#f8fafc')      # Slate 50 (Neutral Background)
        self.accent_green = colors.HexColor('#10b981')  # Success Green
        self.accent_green_light = colors.HexColor('#f0fdf4') # Light Green
        self.accent_orange = colors.HexColor('#f97316') # Warning Orange
        self.accent_orange_light = colors.HexColor('#fff7ed')
        self.accent_red = colors.HexColor('#ef4444')    # Danger Red
        self.accent_red_light = colors.HexColor('#fef2f2')
        self.text_dark = colors.HexColor('#0f172a')     # Slate 900
        self.text_medium = colors.HexColor('#334155')   # Slate 700
        self.text_light = colors.HexColor('#64748b')    # Slate 500
        self.border_color = colors.HexColor('#cbd5e1')  # Slate 300
    
    def _create_header(self, story, styles, invoice_number: str, company_settings: Optional[Dict[str, Any]] = None):
        """Create professional header with Company Name and Invoice Badge."""
        company_name = (company_settings or {}).get('company_name', settings.company_name)
        
        # Left: Company Info
        company_info = Paragraph(
            f'<b><font size=18 color={self.primary_dark}>{company_name}</font></b><br/>'
            f'<font size=9 color={self.text_light}>Professional Manufacturing Solutions</font>',
            ParagraphStyle('CompanyInfo', parent=styles['Normal'], leading=13)
        )

        # Right: Invoice Badge (Blue Box)
        invoice_badge_content = [
            [Paragraph(
                f'<b><font size=12 color=white>INVOICE</font></b><br/>'
                f'<font size=14 color=white><b>#{invoice_number}</b></font>',
                ParagraphStyle('InvoiceBadgeText', parent=styles['Normal'], alignment=TA_CENTER, leading=16)
            )]
        ]
        invoice_badge = Table(invoice_badge_content, colWidths=[70*mm])
        invoice_badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.primary),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))

        # Header Layout Table
        header_data = [[company_info, invoice_badge]]
        header_table = Table(header_data, colWidths=[120*mm, 75*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 4*mm))

    def _create_info_section(self, story, styles, order_data: Dict[str, Any], client_data: Dict[str, Any]):
        """Create two distinct cards for Bill To and Invoice Details."""
        
        # Format dates
        order_date_str = order_data.get('order_date', datetime.now().isoformat())
        try:
            order_date = datetime.fromisoformat(order_date_str.replace('Z', '+00:00'))
        except:
            order_date = datetime.now()
        formatted_date = order_date.strftime('%d %B %Y')
        
        # --- Left Card: BILL TO ---
        bill_to_header = Paragraph(
            '<b><font size=12 color=#1e40af>BILL TO</font></b>',
            ParagraphStyle('CardHeader', parent=styles['Normal'], spaceAfter=0)
        )
        
        bill_to_content = [
            [bill_to_header],
            [Paragraph(f'<b><font size=11>{client_data.get("name", "N/A")}</font></b>', styles['Normal'])],
            [Paragraph(f'<font size=10 color=#64748b>Type: {client_data.get("type", "N/A")}</font>', styles['Normal'])],
            [Paragraph(f'<font size=10 color=#64748b>Contact: {client_data.get("contact", "N/A")}</font>', styles['Normal'])],
            [Paragraph(f'<font size=10 color=#64748b>Address: {client_data.get("address", "N/A")}</font>', styles['Normal'])],
        ]
        
        bill_to_table = Table(bill_to_content, colWidths=[90*mm])
        bill_to_table.setStyle(TableStyle([
            # Header Row Styling
            ('BACKGROUND', (0, 0), (0, 0), self.primary_light),
            ('TOPPADDING', (0, 0), (0, 0), 4),
            ('BOTTOMPADDING', (0, 0), (0, 0), 4),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('LINEBELOW', (0, 0), (0, 0), 1, self.primary),
            # Content Rows Styling
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6), # Extra padding at bottom
            # Border
            ('BOX', (0, 0), (-1, -1), 1, self.border_color),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))

        # --- Right Card: INVOICE DETAILS ---
        details_header = Paragraph(
            '<b><font size=12 color=#1e40af>INVOICE DETAILS</font></b>',
            ParagraphStyle('CardHeader', parent=styles['Normal'], spaceAfter=0)
        )
        
        details_content = [
            [details_header],
            [Paragraph(f'<b>Date:</b> {formatted_date}', ParagraphStyle('DetailText', parent=styles['Normal'], fontSize=10))],
            [Paragraph(f'<b>Status:</b> {order_data.get("status", "Pending")}', ParagraphStyle('DetailText', parent=styles['Normal'], fontSize=10))],
        ]
        
        details_table = Table(details_content, colWidths=[90*mm])
        details_table.setStyle(TableStyle([
            # Header Row Styling
            ('BACKGROUND', (0, 0), (0, 0), self.primary_light),
            ('TOPPADDING', (0, 0), (0, 0), 4),
            ('BOTTOMPADDING', (0, 0), (0, 0), 4),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('LINEBELOW', (0, 0), (0, 0), 1, self.primary),
            # Content Rows Styling
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            # Border
            ('BOX', (0, 0), (-1, -1), 1, self.border_color),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))

        # Layout for Cards
        cards_layout = Table([[bill_to_table, details_table]], colWidths=[95*mm, 95*mm])
        cards_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        story.append(cards_layout)
        story.append(Spacer(1, 3*mm))

    def _create_items_table(self, story, styles, order_data: Dict[str, Any], company_settings: Optional[Dict[str, Any]] = None):
        """Create professional items table with modern styling for multiple items."""
        currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')
        items = order_data.get('items', [])
        
        # Header with columns: Description, Pages, Paper, Qty, Unit Price, Total
        items_data = [
            ['Description', 'Pages', 'Paper', 'Qty', 'Unit Price', 'Total']
        ]
        
        # Add row for each item
        if items and len(items) > 0:
            for item in items:
                pages_display = str(item.get('pages')) if item.get('pages') is not None else 'N/A'
                paper_display = item.get('paper') or 'N/A'
                
                items_data.append([
                    item.get('description', 'Item'),
                    pages_display,
                    paper_display,
                    str(item.get('quantity', 1)),
                    f"{currency_symbol} {item.get('unit_price', 0):,.2f}",
                    f"{currency_symbol} {item.get('total_price', 0):,.2f}"
                ])
        else:
            # Fallback for orders without items (backward compatibility)
            total_amount = order_data.get('total_amount', 0)
            pages = order_data.get('pages')
            paper = order_data.get('paper')
            
            pages_display = str(pages) if pages is not None else 'N/A'
            paper_display = paper if paper else 'N/A'
            
            items_data.append([
                'Product / Service Order',
                pages_display,
                paper_display,
                '1',
                f"{currency_symbol} {total_amount:,.2f}",
                f"{currency_symbol} {total_amount:,.2f}"
            ])
        
        # Adjusted column widths to fit A4 (total ~190mm)
        # Description: 55mm, Pages: 18mm, Paper: 30mm, Qty: 15mm, Unit Price: 36mm, Total: 36mm
        items_table = Table(items_data, colWidths=[55*mm, 18*mm, 30*mm, 15*mm, 36*mm, 36*mm])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),      # Description - left
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),    # Pages - center
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),      # Paper - left
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),    # Qty - center
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),    # Unit Price & Total - right
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Rows
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_color),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_light]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 3*mm))
        
        # Totals Section (Modern Card Style)
        total_amount = order_data.get('total_amount', 0)
        totals_data = [
            ['Subtotal:', f"{currency_symbol} {total_amount:,.2f}"],
            ['Tax (0%):', f"{currency_symbol} 0.00"],
            ['Total:', f"{currency_symbol} {total_amount:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[50*mm, 40*mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_medium),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            # Total Row Styling
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.primary_dark),
            ('LINEABOVE', (0, -1), (-1, -1), 1, self.border_color),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
        ]))
        
        # Container for totals (Right aligned with background)
        totals_container = Table([[None, totals_table]], colWidths=[100*mm, 90*mm])
        totals_container.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BACKGROUND', (1, 0), (1, 0), self.bg_light),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ('TOPPADDING', (1, 0), (1, 0), 8),
            ('BOTTOMPADDING', (1, 0), (1, 0), 8),
            ('RIGHTPADDING', (1, 0), (1, 0), 8),
        ]))
        
        story.append(totals_container)
        story.append(Spacer(1, 4*mm))

    def _create_payment_summary(self, story, styles, order_data: Dict[str, Any], payment_history: Optional[List[Dict[str, Any]]], company_settings: Optional[Dict[str, Any]] = None):
        """Create payment summary with clear deduction display showing amount received subtracted from total."""

        currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')

        # Get order totals from order_data (these are the source of truth)
        total_amount = float((order_data or {}).get('total_amount', 0))
        total_paid = float((order_data or {}).get('paid_amount', 0))
        balance_due = float((order_data or {}).get('balance', total_amount - total_paid))

        # If payment_history exists, calculate from it (fallback)
        if payment_history and len(payment_history) > 0:
            calculated_paid = sum(float(p.get('amount', 0)) for p in payment_history)
            if calculated_paid > 0:
                total_paid = calculated_paid
                balance_due = total_amount - total_paid

        # Only show payment summary if there are payments made
        if total_paid <= 0:
            return

        # Section Header with icon
        story.append(Paragraph(
            f'<b><font color=#1e40af>■ PAYMENT SUMMARY</font></b>',
            ParagraphStyle('SummaryHeader', parent=styles['Normal'], fontSize=12, spaceAfter=2)
        ))
        story.append(Spacer(1, 2*mm))

        # Create 3-column payment summary table matching reference image style
        # Headers
        headers = [
            Paragraph('<b>Total Order Amount</b>', ParagraphStyle('H1', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=self.text_medium)),
            Paragraph('<b>Total Paid to Date</b>', ParagraphStyle('H2', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=self.text_medium)),
            Paragraph('<b>Remaining Balance</b>', ParagraphStyle('H3', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=self.text_medium)),
        ]

        # Values with color coding: Red for total, Green for paid, Orange for balance
        values = [
            Paragraph(f'<b><font size=13 color=#ef4444>{currency_symbol} {total_amount:,.2f}</font></b>',
                     ParagraphStyle('V1', parent=styles['Normal'], alignment=TA_CENTER)),
            Paragraph(f'<b><font size=13 color=#10b981>{currency_symbol} {total_paid:,.2f}</font></b>',
                     ParagraphStyle('V2', parent=styles['Normal'], alignment=TA_CENTER)),
            Paragraph(f'<b><font size=13 color=#f97316>{currency_symbol} {balance_due:,.2f}</font></b>',
                     ParagraphStyle('V3', parent=styles['Normal'], alignment=TA_CENTER)),
        ]

        summary_data = [headers, values]
        summary_table = Table(summary_data, colWidths=[63*mm, 63*mm, 64*mm])
        summary_table.setStyle(TableStyle([
            # General alignment
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Border styling - blue borders
            ('GRID', (0, 0), (-1, -1), 1, self.primary),
            ('BOX', (0, 0), (-1, -1), 1.5, self.primary),
            # Header Row - light blue background
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_light),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Value Row - color-coded backgrounds matching the text colors
            ('BACKGROUND', (0, 1), (0, 1), self.accent_red_light),    # Light red for Total
            ('BACKGROUND', (1, 1), (1, 1), self.accent_green_light),  # Light green for Paid
            ('BACKGROUND', (2, 1), (2, 1), self.accent_orange_light), # Light orange for Balance
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 4*mm))

    def _create_footer(self, story, styles, company_settings: Optional[Dict[str, Any]] = None):
        """Create professional footer."""
        
        # QR Code and Thank You Message side-by-side
        # We need to generate QR here or pass it. Let's assume we generate it in generate_invoice and pass it, 
        # or just generate it here if we have data. 
        # Since this method doesn't have order data, we'll just put the container structure 
        # and let generate_invoice handle the QR insertion if possible, OR we modify signature.
        # To keep it simple and consistent with previous code, let's just do the text part here 
        # and let generate_invoice append the QR code before calling this, or we move QR logic here.
        # Actually, the previous code had QR logic in generate_invoice. 
        # Let's make a container for QR + Text.
        pass # Handled in generate_invoice to access order_data for QR

    def generate_invoice(self, order_data: Dict[str, Any], client_data: Dict[str, Any], company_settings: Optional[Dict[str, Any]] = None, payment_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate professional invoice PDF."""
        invoice_number = order_data.get('order_number', '')
        invoice_date = datetime.now().strftime('%Y-%m-%d')
        
        filename = f"invoice_{invoice_number}_{invoice_date}.pdf"
        filepath = os.path.join(self.invoice_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=12*mm,
            leftMargin=12*mm,
            topMargin=12*mm,
            bottomMargin=12*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        self._create_header(story, styles, invoice_number, company_settings)
        self._create_info_section(story, styles, order_data, client_data)
        self._create_items_table(story, styles, order_data, company_settings)
        self._create_payment_summary(story, styles, order_data, payment_history, company_settings)
        
        # Footer Section (QR + Thank You + Bottom Bar)
        # QR Code
        qr_img = None
        try:
            total_amount = order_data.get('total_amount', 0)
            qr_data = f"INVOICE:{invoice_number}|AMT:{total_amount}"
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
            Paragraph('<b>Thank You for Your Business!</b>', ParagraphStyle('TY1', parent=styles['Normal'], fontSize=8, textColor=self.primary_dark)),
            Paragraph('Payment is due within 30 days. Please include invoice number on your check.', ParagraphStyle('TY2', parent=styles['Normal'], fontSize=7, textColor=self.text_light)),
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
invoice_generator = ProfessionalInvoiceGenerator()
