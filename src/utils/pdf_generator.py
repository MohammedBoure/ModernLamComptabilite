import os
import json
from PySide6.QtGui import QPainter, QPageSize, QPageLayout, QColor, QFont, QPixmap, QTextDocument
from PySide6.QtCore import Qt, QRectF, QMarginsF
from PySide6.QtPrintSupport import QPrinter

class PdfGenerator:
    def __init__(self, settings_path="pdf_settings.json"):
        self.settings_path = settings_path
        self.settings = self.load_settings()
        
    def load_settings(self):
        defaults = {
            "theme_color": "#007572",
            "doc_title": "MODERNLAM",
            "banner_height_cm": 4.8, 
            "banner_path": "",
            "banner_img_x_cm": 0.0,
            "banner_img_y_cm": 0.0,
            "banner_img_w_cm": 21.0,
            "banner_img_h_cm": 4.8,
            "table_start_y_cm": 8.0,
            "footer_left_label": "Signature de l'Agent",
            "footer_right_label": "Visa Direction",
            "nif": "",
            "rip": ""
        }
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {**defaults, **data}
            except:
                pass
        return defaults

    def generate_pdf(self, output_path, title_suffix, table_html):
        """
        Generate a PDF with the custom header and an HTML table.
        output_path: str, the file path to save the PDF.
        title_suffix: str, appended to doc_title (e.g. " - Octobre 2026").
        table_html: str, the HTML string of the <table> to render.
        """
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(output_path)
        
        # Setup page layout
        page_layout = QPageLayout()
        page_layout.setPageSize(QPageSize(QPageSize.A4))
        page_layout.setOrientation(QPageLayout.Portrait)
        page_layout.setMargins(QMarginsF(0, 0, 0, 0)) # No margins to draw the banner exactly at X=0 Y=0
        printer.setPageLayout(page_layout)
        
        painter = QPainter(printer)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Conversions (HighResolution is usually 1200 dpi)
        # 1 cm = 0.3937 inches
        # dots per cm = 1200 * 0.3937 = 472.44
        dpcm = printer.resolution() / 2.54
        
        s = self.settings
        color = QColor(s.get('theme_color', "#007572"))
        
        # 1. Draw Banner
        banner_path = s.get('banner_path', "")
        if banner_path and os.path.exists(banner_path):
            img_x = s.get('banner_img_x_cm', 0.0) * dpcm
            img_y = s.get('banner_img_y_cm', 0.0) * dpcm
            img_w = s.get('banner_img_w_cm', 21.0) * dpcm
            img_h = s.get('banner_img_h_cm', 4.8) * dpcm
            pixmap = QPixmap(banner_path)
            if not pixmap.isNull():
                painter.drawPixmap(QRectF(img_x, img_y, img_w, img_h), pixmap, QRectF(pixmap.rect()))
        
        # 2. Draw Title
        total_h_cm = s.get('banner_height_cm', 4.8)
        title_y = (total_h_cm + 1.0) * dpcm
        
        painter.setPen(color)
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        full_title = f"{s.get('doc_title', '')}{title_suffix}"
        
        # We will use small margins so the table and title take almost full width
        table_x = 0.5 * dpcm
        table_w = 20.0 * dpcm
        
        painter.drawText(QRectF(table_x, title_y - dpcm, table_w, 2.0 * dpcm), Qt.AlignLeft | Qt.AlignVCenter, full_title)
        
        # Draw NIF and RIP metadata line if present
        nif = s.get('nif', '')
        rip = s.get('rip', '')
        meta_parts = []
        if nif:
            meta_parts.append(f"NIF: {nif}")
        if rip:
            meta_parts.append(f"RIP: {rip}")
        if meta_parts:
            meta_text = "   |   ".join(meta_parts)
            painter.setPen(Qt.gray)
            painter.setFont(QFont("Arial", 10, QFont.Normal))
            painter.drawText(QRectF(table_x, title_y + 0.8 * dpcm, table_w, 0.5 * dpcm), Qt.AlignLeft | Qt.AlignVCenter, meta_text)
        
        # 3. Draw Table HTML using QTextDocument
        table_start_y = s.get('table_start_y_cm', 8.0) * dpcm
        
        # Base HTML wrapper to set styles and ensure the table takes full width
        full_html = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 10pt; color: #333; margin: 0; padding: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: {color.name()}; color: white; padding: 5px; text-align: left; font-weight: bold; border: 1px solid #ddd; }}
            td {{ padding: 4px 5px; border: 1px solid #ddd; }}
            .right {{ text-align: right; }}
            .center {{ text-align: center; }}
        </style>
        </head>
        <body>
        {table_html}
        </body>
        </html>
        """
        
        scale = printer.resolution() / 96.0
        doc = QTextDocument()
        doc.setHtml(full_html)
        doc.setTextWidth(table_w / scale)
        
        # Translate painter to table start and draw
        painter.translate(table_x, table_start_y)
        painter.save()
        painter.scale(scale, scale)
        doc.drawContents(painter)
        painter.restore()
        painter.translate(-table_x, -table_start_y)
        
        # 4. Draw Footer
        # Since we might have multiple pages if the table is long, 
        # QTextDocument paginates automatically if we manage the painter translation,
        # but for simplicity, we assume single page for monthly reports or draw footer at absolute bottom of A4.
        page_height = 29.7 * dpcm
        footer_y = page_height - 2.5 * dpcm
        
        painter.setPen(Qt.black)
        font_footer = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font_footer)
        painter.drawText(QRectF(table_x, footer_y, 9.0 * dpcm, 1.0 * dpcm), Qt.AlignLeft, s.get('footer_left_label', ''))
        painter.drawText(QRectF(table_x + 11.0 * dpcm, footer_y, 9.0 * dpcm, 1.0 * dpcm), Qt.AlignRight, s.get('footer_right_label', ''))
        
        painter.end()
        return True
