from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
import io
from datetime import datetime
from typing import Dict, Any, Optional
from config import get_settings
import os

settings = get_settings()

class InvoiceGenerator:
    def __init__(self):
        self.invoice_dir = settings.invoice_dir
        os.makedirs(self.invoice_dir, exist_ok=True)
    
    def generate_invoice(self, order_data: Dict[str, Any], client_data: Dict[str, Any], company_settings: Optional[Dict[str, Any]] = None) -> str:
        """Generate an invoice PDF for an order with dynamic company branding."""
        invoice_number = order_data.get('order_number', '')
        invoice_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create filename
        filename = f"invoice_{invoice_number}_{invoice_date}.pdf"
        filepath = os.path.join(self.invoice_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Use dynamic settings from database or fallback to config
        company_name = (company_settings or {}).get('company_name', settings.company_name)
        company_address = (company_settings or {}).get('company_address', settings.company_address)
        company_phone = (company_settings or {}).get('company_phone', settings.company_phone)
        company_email = (company_settings or {}).get('company_email', settings.company_email)
        currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')
        
        # Header
        header_text = f"<b>{company_name}</b>"
        story.append(Paragraph(header_text, title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Company Info
        company_info = f"""
        <b>Address:</b> {company_address}<br/>
        <b>Phone:</b> {company_phone}<br/>
        <b>Email:</b> {company_email}
        """
        story.append(Paragraph(company_info, styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Invoice Info
        invoice_info_data = [
            ['INVOICE', f''],
            ['Invoice Number:', invoice_number],
            ['Date:', invoice_date],
            ['Status:', order_data.get('status', 'Pending')]
        ]
        
        invoice_info_table = Table(invoice_info_data, colWidths=[2*inch, 2*inch])
        invoice_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(invoice_info_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Bill To Section
        bill_to_data = [
            ['Bill To:'],
            ['', f"<b>{client_data.get('name', '')}</b>"],
            ['', f"Type: {client_data.get('type', '')}"],
            ['', client_data.get('address', '')],
            ['', f"Contact: {client_data.get('contact', '')}"]
        ]
        
        bill_to_table = Table(bill_to_data, colWidths=[2*inch, 3*inch])
        bill_to_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(bill_to_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Order Items Table
        items_data = [
            ['Description', 'Quantity', 'Unit Price', 'Total']
        ]
        
        # Add order items (placeholder - you would get this from order_data)
        items_data.extend([
            ['Product/Service', '1', f"{order_data.get('total_amount', 0)}", f"{order_data.get('total_amount', 0)}"]
        ])
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Totals
        total_amount = order_data.get('total_amount', 0)
        tax = 0  # You can calculate tax based on your requirements
        final_total = total_amount + tax
        
        totals_data = [
            ['Subtotal:', f"{total_amount:.2f}"],
            ['Tax:', f"{tax:.2f}"],
            ['<b>TOTAL:</b>', f"<b>{final_total:.2f}</b>"]
        ]
        
        totals_table = Table(totals_data, colWidths=[2*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph(f'<i>All amounts in {currency_symbol}</i>', styles['Italic']))
        story.append(Spacer(1, 0.2*inch))
        story.append(totals_table)
        story.append(Spacer(1, 0.5*inch))
        
        # QR Code
        try:
            qr_data = f"Invoice: {invoice_number}, Amount: {final_total}"
            qr = qrcode.QRCode(version=1, box_size=3, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color='black', back_color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            qr_img = Image(img_buffer, width=100, height=100)
            story.append(Paragraph('<b>Verification QR Code:</b>', styles['Normal']))
            story.append(qr_img)
        except Exception as e:
            print(f"Error generating QR code: {e}")
        
        story.append(Spacer(1, 0.3*inch))
        
        # Footer with company details
        footer_text = f"""
        <b>{company_name}</b><br/>
        <i>Address: {company_address}<br/>
        Phone: {company_phone} | Email: {company_email}<br/>
        Thank you for your business!</i>
        """
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)))
        
        # Build PDF
        doc.build(story)
        
        return filepath

# Global instance
invoice_generator = InvoiceGenerator()

