import os
import json
from PySide6.QtGui import QPainter, QPageSize, QPageLayout, QColor, QFont, QPixmap, QTextDocument, QAbstractTextDocumentLayout, QPen
from PySide6.QtCore import Qt, QRectF, QMarginsF, QSizeF
from PySide6.QtPrintSupport import QPrinter

class PdfGenerator:
    def __init__(self, settings_path="pdf_settings.json"):
        self.settings_path = settings_path
        self.settings = self.load_settings()
        
    def load_settings(self):
        defaults = {
            "theme_color": "#007572",
            "doc_title": "MODERNLAM",
            "banner_height_cm": 4.5, 
            "banner_path": "",
            "banner_img_x_cm": 0.0,
            "banner_img_y_cm": 0.0,
            "banner_img_w_cm": 21.0,
            "banner_img_h_cm": 4.5,
            "table_start_y_cm": 8.0,
            "footer_left_label": "Signature & Cachet de l'Agent",
            "footer_right_label": "Visa & Cachet de la Direction",
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
        Generate a multi-page PDF with custom header and spacious signature stamp footer on EVERY page.
        """
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(output_path)
        
        page_layout = QPageLayout(QPageSize(QPageSize.A4), QPageLayout.Portrait, QMarginsF(0, 0, 0, 0))
        printer.setPageLayout(page_layout)
        
        painter = QPainter(printer)
        painter.setRenderHint(QPainter.Antialiasing)
        
        res = printer.resolution()
        dpcm = res / 2.54

        s = self.settings
        theme_color = QColor(s.get('theme_color', "#007572"))

        page_w_dots = 21.0 * dpcm
        page_h_dots = 29.7 * dpcm

        header_height_cm = s.get('banner_height_cm', 4.5)
        top_margin_dots = (header_height_cm + 0.8) * dpcm
        bottom_margin_dots = 4.2 * dpcm  # Reserved ample vertical space for stamps & signatures
        left_margin_dots = 1.0 * dpcm
        right_margin_dots = 1.0 * dpcm

        content_w_dots = page_w_dots - left_margin_dots - right_margin_dots
        content_h_dots = page_h_dots - top_margin_dots - bottom_margin_dots

        # Scale factor (96 DPI standard screen base)
        scale = res / 96.0
        doc_w_pts = content_w_dots / scale
        doc_h_pts = content_h_dots / scale

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #1e293b;
                margin: 0;
                padding: 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
                margin-bottom: 12px;
                page-break-inside: auto;
            }}
            tr {{
                page-break-inside: avoid;
                page-break-after: auto;
            }}
            thead {{
                display: table-header-group;
            }}
            th {{
                background-color: {theme_color.name()};
                color: white;
                padding: 6px;
                text-align: left;
                font-weight: bold;
                border: 1px solid #cbd5e1;
            }}
            td {{
                padding: 5px 6px;
                border: 1px solid #cbd5e1;
            }}
            h2, h3 {{
                page-break-after: avoid;
            }}
        </style>
        </head>
        <body>
        {table_html}
        </body>
        </html>
        """

        doc = QTextDocument()
        doc.setHtml(full_html)
        doc.setTextWidth(doc_w_pts)
        doc.setPageSize(QSizeF(doc_w_pts, doc_h_pts))

        page_count = doc.pageCount()

        for page_idx in range(page_count):
            if page_idx > 0:
                printer.newPage()

            # --------------------------------------------------
            # 1. DRAW EN-TÊTE (HEADER BANNER) ON EVERY PAGE
            # --------------------------------------------------
            banner_path = s.get('banner_path', "")
            if banner_path and os.path.exists(banner_path):
                img_x = s.get('banner_img_x_cm', 0.0) * dpcm
                img_y = s.get('banner_img_y_cm', 0.0) * dpcm
                img_w = s.get('banner_img_w_cm', 21.0) * dpcm
                img_h = s.get('banner_img_h_cm', 4.5) * dpcm
                pixmap = QPixmap(banner_path)
                if not pixmap.isNull():
                    painter.drawPixmap(QRectF(img_x, img_y, img_w, img_h), pixmap, QRectF(pixmap.rect()))
            else:
                # Default Modern Header Banner
                painter.fillRect(QRectF(0, 0, page_w_dots, 1.2 * dpcm), theme_color)
                painter.setPen(Qt.white)
                painter.setFont(QFont("Arial", 11, QFont.Bold))
                painter.drawText(QRectF(1.0 * dpcm, 0, page_w_dots - 2.0 * dpcm, 1.2 * dpcm), Qt.AlignLeft | Qt.AlignVCenter, s.get('doc_title', 'MODERNLAM'))

            # Header Title Line
            title_y = (header_height_cm + 0.1) * dpcm
            painter.setPen(theme_color)
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            full_title = f"{s.get('doc_title', '')}{title_suffix}"
            painter.drawText(QRectF(left_margin_dots, title_y, content_w_dots, 0.7 * dpcm), Qt.AlignLeft | Qt.AlignVCenter, full_title)

            # NIF / RIP / Subtitle metadata if available
            nif = s.get('nif', '')
            rip = s.get('rip', '')
            meta_parts = []
            if nif: meta_parts.append(f"NIF: {nif}")
            if rip: meta_parts.append(f"RIP: {rip}")
            if meta_parts:
                meta_text = "   |   ".join(meta_parts)
                painter.setPen(QColor("#64748b"))
                painter.setFont(QFont("Arial", 9, QFont.Normal))
                painter.drawText(QRectF(left_margin_dots, title_y + 0.6 * dpcm, content_w_dots, 0.4 * dpcm), Qt.AlignLeft | Qt.AlignVCenter, meta_text)

            # --------------------------------------------------
            # 2. DRAW SPACIOUS STAMP & SIGNATURE BOXES ON EVERY PAGE
            # --------------------------------------------------
            footer_y = page_h_dots - 3.8 * dpcm
            box_w = 8.5 * dpcm
            box_h = 2.6 * dpcm  # Generous physical height for stamp & signature

            # Left Signature & Stamp Box
            left_x = left_margin_dots
            painter.setPen(QPen(QColor("#cbd5e1"), 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(QRectF(left_x, footer_y, box_w, box_h), 4, 4)

            painter.setPen(theme_color)
            painter.setFont(QFont("Arial", 9.5, QFont.Bold))
            painter.drawText(QRectF(left_x + 0.3 * dpcm, footer_y + 0.2 * dpcm, box_w - 0.6 * dpcm, 0.5 * dpcm), Qt.AlignLeft | Qt.AlignVCenter, s.get('footer_left_label', 'Signature & Cachet de l\'Agent'))

            # Right Signature & Stamp Box
            right_x = left_margin_dots + content_w_dots - box_w
            painter.setPen(QPen(QColor("#cbd5e1"), 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(QRectF(right_x, footer_y, box_w, box_h), 4, 4)

            painter.setPen(theme_color)
            painter.setFont(QFont("Arial", 9.5, QFont.Bold))
            painter.drawText(QRectF(right_x + 0.3 * dpcm, footer_y + 0.2 * dpcm, box_w - 0.6 * dpcm, 0.5 * dpcm), Qt.AlignRight | Qt.AlignVCenter, s.get('footer_right_label', 'Visa & Cachet de la Direction'))

            # Page numbering Line below signature boxes
            page_num_y = footer_y + box_h + 0.15 * dpcm
            painter.setPen(QColor("#64748b"))
            painter.setFont(QFont("Arial", 8.5, QFont.Normal))
            painter.drawText(QRectF(left_margin_dots, page_num_y, content_w_dots, 0.4 * dpcm), Qt.AlignCenter, f"Page {page_idx + 1} / {page_count}")

            # --------------------------------------------------
            # 3. DRAW PAGE CONTENT FOR THIS PAGE
            # --------------------------------------------------
            painter.save()
            painter.translate(left_margin_dots, top_margin_dots)
            painter.scale(scale, scale)
            painter.translate(0, -page_idx * doc_h_pts)
            
            ctx = QAbstractTextDocumentLayout.PaintContext()
            ctx.clip = QRectF(0, page_idx * doc_h_pts, doc_w_pts, doc_h_pts)
            doc.documentLayout().draw(painter, ctx)
            painter.restore()

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

    def generate_rapport_comptabilite_pdf(self, output_path, month_name, year, data):
        """
        Generate full official PDF matching 'excel/01) Rapport de comptabilité Décembre 2025.docx'
        """
        rev = data['revenus']
        dep = data['depenses']
        res = data['resultat']

        html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 10pt; color: #1e293b;">
            <div style="text-align: center; border-bottom: 2px solid #007572; padding-bottom: 8px; margin-bottom: 12px;">
                <h2 style="margin: 0; color: #007572; font-size: 16pt;">RAPPORT DE COMPTABILITÉ – {month_name.upper()} {year}</h2>
                <p style="margin: 3px 0 0 0; font-size: 9pt; color: #64748b;">Laboratoire d'Analyses Médicales MODERNLAM | Agrément N° 2024/08 DSP JIJEL</p>
            </div>

            <!-- SECTION I: REVENUS -->
            <h3 style="color: #007572; border-bottom: 1px solid #007572; padding-bottom: 3px; margin-top: 10px; margin-bottom: 8px;">I. RAPPORT DES REVENUS</h3>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 9.5pt;">
                <thead>
                    <tr style="background-color: #007572; color: white;">
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 40px;">N°</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Catégorie / Désignation</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; width: 160px;">Montant Hors Taxe (DA)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">01</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">Les Revenus de Clientèle Ville</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{rev['ville']:,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">02</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">Sous-Traitance (Conventions & Partenaires)</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{rev['total_st']:,.2f} DA</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">03</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">Revenus Supplémentaires (Coffre)</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{rev['total_supp']:,.2f} DA</td>
                    </tr>
                    <tr style="background-color: #e3f2fd; font-weight: bold; color: #1565c0;">
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">04</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1;">Chiffre d'Affaires Mensuel Total</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right;">{rev['chiffre_affaires']:,.2f} DA</td>
                    </tr>
                </tbody>
            </table>

            <!-- SECTION II: DÉPENSES -->
            <h3 style="color: #b91c1c; border-bottom: 1px solid #b91c1c; padding-bottom: 3px; margin-top: 10px; margin-bottom: 8px;">II. RAPPORT DES DÉPENSES</h3>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 9.5pt;">
                <thead>
                    <tr style="background-color: #b91c1c; color: white;">
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 40px;">N°</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Catégorie de Dépense</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; width: 130px;">Montant Payé (DA)</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; width: 130px;">Montant Dette (DA)</th>
                    </tr>
                </thead>
                <tbody>
        """

        idx = 1
        for cat_name, cat_info in dep['categories'].items():
            bg = "#f8fafc" if idx % 2 == 1 else "#ffffff"
            html += f"""
                    <tr style="background-color: {bg};">
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">{idx:02d}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">{cat_name}</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">{cat_info['paye']:,.2f} DA</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">{cat_info['dette']:,.2f} DA</td>
                    </tr>
            """
            idx += 1

        html += f"""
                    <tr style="background-color: #ffebee; font-weight: bold; color: #b91c1c;">
                        <td colspan="2" style="padding: 6px; border: 1px solid #cbd5e1;">Charges Totales Mensuelles</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right;">{dep['total_paye']:,.2f} DA</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right;">{dep['total_dette']:,.2f} DA</td>
                    </tr>
                    <tr style="background-color: #fee2e2; font-weight: bold; color: #991b1b;">
                        <td colspan="2" style="padding: 6px; border: 1px solid #cbd5e1;">TOTAL DÉPENSES GLOBAL (Payé + Dette)</td>
                        <td colspan="2" style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; font-size: 11pt;">{dep['total_global']:,.2f} DA</td>
                    </tr>
                </tbody>
            </table>

            <!-- SECTION III: RÉSULTAT FINAL -->
            <h3 style="color: #1e293b; border-bottom: 1px solid #1e293b; padding-bottom: 3px; margin-top: 10px; margin-bottom: 8px;">III. RÉSULTAT FINAL & PROFITABILITÉ</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 9.5pt;">
                <thead>
                    <tr style="background-color: #334155; color: white;">
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 40px;">N°</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Désignation</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; width: 130px;">Crédit (DA)</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; width: 130px;">Débit (DA)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">01</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">Les Revenus de Clientèle Ville</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{rev['ville']:,.2f} DA</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">-</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">02</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">Sous-Traitance</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{rev['total_st']:,.2f} DA</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">-</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">03</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1;">Les Revenus Supplémentaires</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{rev['total_supp']:,.2f} DA</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">-</td>
                    </tr>
                    <tr style="background-color: #fff1f2;">
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: center;">04</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; font-weight: bold; color: #b91c1c;">Charges Totales Globales</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right;">-</td>
                        <td style="padding: 5px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold; color: #b91c1c;">{dep['total_global']:,.2f} DA</td>
                    </tr>
                    <tr style="background-color: #f0fdf4; font-weight: bold;">
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">05</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; color: #15803d;">Profitabilité Nette Mensuelle</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right; color: #15803d;">{res['profitabilite_nette']:,.2f} DA</td>
                        <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right;">-</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        title_suffix = f" - Rapport de Comptabilité ({month_name} {year})"
        return self.generate_pdf(output_path, title_suffix, html)



