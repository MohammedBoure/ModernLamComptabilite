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

    def generate_analytique_achats_pdf(self, output_path, month_name, year, data):
        """
        Generate PDF matching '02) Rapport Analytic des Achats' Word file.
        data: dict with 'total_achats' and 'categories' list of dicts {'categorie', 'montant', 'pourcentage'}.
        """
        total_achats = data.get('total_achats', 0.0)
        categories = data.get('categories', [])

        html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 11pt;">
            <div style="background-color: #f8fafc; padding: 12px; border: 1px solid #cbd5e1; border-radius: 4px; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #007572; font-size: 14pt;">Analytiques des Achats du Mois de {month_name} {year}</h3>
                <p style="margin: 5px 0 0 0; font-weight: bold; font-size: 12pt; color: #1e293b;">
                    Les Achats globaux du Mois de {month_name} {year} : <span style="color: #007572;">{total_achats:,.2f} DA</span>
                </p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background-color: #007572; color: white;">
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: left;">Catégorie d'Achat / Dépense</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: right; width: 180px;">Montant (DA)</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: right; width: 140px;">Part (%)</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for c in categories:
            cat_name = c.get('categorie', '')
            montant = c.get('montant', 0.0)
            pct = c.get('pourcentage', 0.0)
            html += f"""
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; font-weight: 500;">{cat_name}</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{montant:,.2f} DA</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; color: #007572; font-weight: bold;">{pct:.2f} %</td>
                    </tr>
            """
            
        html += f"""
                    <tr style="background-color: #f1f5f9; font-weight: bold;">
                        <td style="padding: 8px; border: 1px solid #cbd5e1;">TOTAL ACHATS GLOBAUX</td>
                        <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right; color: #007572;">{total_achats:,.2f} DA</td>
                        <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right; color: #007572;">100.00 %</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        title_suffix = f" - Rapport Analytique des Achats ({month_name} {year})"
        return self.generate_pdf(output_path, title_suffix, html)

    def generate_incineration_pdf(self, output_path, month_name, year, rows, stats):
        """
        Generate PDF matching 'Etat SNC Station d'Incinération Benniou MODERNLAM' Excel file.
        rows: list of dicts from Station_Incineration
        stats: dict from get_incineration_stats
        """
        html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h3 style="margin-top: 0; color: #007572; font-size: 13pt; text-align: center;">
                ETAT SNC STATION D'INCINÉRATION BENNIOU ({month_name.upper()} {year})
            </h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10pt;">
                <thead>
                    <tr style="background-color: #007572; color: white;">
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; width: 40px;">N°</th>
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">Date</th>
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">Date de Remise</th>
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: right;">Poids (KG)</th>
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: right;">Montant (DA)</th>
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">Paiement</th>
                        <th style="padding: 6px; border: 1px solid #cbd5e1; text-align: left;">Observations</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, r in enumerate(rows, start=1):
            date_s = str(r.get('date_suivi', ''))
            date_r = str(r.get('date_remise', '')) if r.get('date_remise') else '-'
            poids = float(r.get('poids_kg', 0))
            montant = float(r.get('montant_total', 0))
            etat = "Payé" if r.get('etat_paiement') == 'PAYE' else "Non payé"
            obs = r.get('observations', '') or '-'
            bg_color = "#ffffff" if i % 2 != 0 else "#f8fafc"
            
            html += f"""
                    <tr style="background-color: {bg_color};">
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">{i}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">{date_s}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">{date_r}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{poids:.2f}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{montant:,.2f}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center; color: {'green' if etat == 'Payé' else '#dc2626'}; font-weight: bold;">{etat}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">{obs}</td>
                    </tr>
            """
            
        tot_poids = stats.get('total_poids_kg', 0.0)
        tot_mnt = stats.get('total_montant', 0.0)
        tot_np = stats.get('total_non_paye', 0.0)
        max_p = stats.get('max_poids_kg', 0.0)
        min_p = stats.get('min_poids_kg', 0.0)
        avg_p = stats.get('moyenne_poids_kg', 0.0)

        html += f"""
                    <tr style="background-color: #e2e8f0; font-weight: bold;">
                        <td colspan="3" style="padding: 6px; border: 1px solid #cbd5e1;">TOTAL</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right; color: #007572;">{tot_poids:.2f} KG</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right; color: #007572;">{tot_mnt:,.2f} DA</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; color: #dc2626;">Non payé: {tot_np:,.2f} DA</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1;">-</td>
                    </tr>
                    <tr style="background-color: #f1f5f9;">
                        <td colspan="3" style="padding: 5px; border: 1px solid #cbd5e1; font-weight: bold;">MAX</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">{max_p:.2f} KG</td>
                        <td colspan="3" style="padding: 5px; border: 1px solid #cbd5e1;">-</td>
                    </tr>
                    <tr style="background-color: #f1f5f9;">
                        <td colspan="3" style="padding: 5px; border: 1px solid #cbd5e1; font-weight: bold;">MIN</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">{min_p:.2f} KG</td>
                        <td colspan="3" style="padding: 5px; border: 1px solid #cbd5e1;">-</td>
                    </tr>
                    <tr style="background-color: #f1f5f9;">
                        <td colspan="3" style="padding: 5px; border: 1px solid #cbd5e1; font-weight: bold;">MOYENNE</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">{avg_p:.2f} KG</td>
                        <td colspan="3" style="padding: 5px; border: 1px solid #cbd5e1;">-</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        title_suffix = f" - Station d'Incinération Benniou ({month_name} {year})"
        return self.generate_pdf(output_path, title_suffix, html)

    def generate_profitabilite_pdf(self, output_path, month_name, year, summary):
        """
        Generate PDF for Mouvement Profitabilité summary.
        summary: dict returned by get_profitability_summary
        """
        prof_val = summary.get('profitability', 0.0)
        prof_pct = summary.get('profitability_pct', 0.0)
        prof_color = "#2e7d32" if prof_val >= 0 else "#c62828"

        html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 11pt;">
            <div style="background-color: #f8fafc; padding: 12px; border: 1px solid #cbd5e1; border-radius: 4px; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #007572; font-size: 14pt;">Mouvement Profitabilité - {month_name} {year}</h3>
                <p style="margin: 5px 0 0 0; font-size: 11pt; color: #475569;">
                    Bilan financier mensuel comparatif (Revenus vs Taux de Charges)
                </p>
            </div>

            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background-color: #007572; color: white;">
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: left;">Indicateur Financier</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: right; width: 220px;">Valeur (DA)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">PAIE ESTIMATION (Salaires)</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('total_paie', 0.0):,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">DEPENSES INTERNE (Caisse)</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('total_dep_int', 0.0):,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">MOUVEMENTS FOURNISSEURS</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('total_cmd', 0.0):,.2f} DA</td>
                    </tr>
                    <tr style="background-color: #ffebee; font-weight: bold; color: #c62828;">
                        <td style="padding: 8px; border: 1px solid #cbd5e1;">TOTAL CHARGES (Fournisseurs + Dépenses + Paie)</td>
                        <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right;">{summary.get('total_costs', 0.0):,.2f} DA</td>
                    </tr>
                    <tr><td colspan="2" style="padding: 4px; border: none;"></td></tr>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">CA LAM (Caisse Ville & TPE)</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('ca_lam', 0.0):,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">CA C (Convention / Mutuelle)</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('ca_c', 0.0):,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">CA ST (Sous-Traitants)</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('ca_st', 0.0):,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1;">ENTREES SUPP (Coffre)</td>
                        <td style="padding: 7px 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{summary.get('entrees_supp', 0.0):,.2f} DA</td>
                    </tr>
                    <tr style="background-color: #e3f2fd; font-weight: bold; color: #1565c0;">
                        <td style="padding: 8px; border: 1px solid #cbd5e1;">CHIFFRE D'AFFAIRES TOTAL</td>
                        <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right;">{summary.get('chiffre_affaire', 0.0):,.2f} DA</td>
                    </tr>
                    <tr><td colspan="2" style="padding: 4px; border: none;"></td></tr>
                    <tr style="background-color: #f1f5f9; font-weight: bold;">
                        <td style="padding: 9px; border: 1px solid #cbd5e1; font-size: 12pt;">PROFITABILITÉ NETTE</td>
                        <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: right; color: {prof_color}; font-size: 12pt;">{prof_val:,.2f} DA</td>
                    </tr>
                    <tr style="background-color: #f1f5f9; font-weight: bold;">
                        <td style="padding: 9px; border: 1px solid #cbd5e1; font-size: 12pt;">% PROFITABILITÉ / CHIFFRE D'AFFAIRE</td>
                        <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: right; color: {prof_color}; font-size: 12pt;">{prof_pct:.2f} %</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        title_suffix = f" - Mouvement Profitabilité ({month_name} {year})"
        return self.generate_pdf(output_path, title_suffix, html)


