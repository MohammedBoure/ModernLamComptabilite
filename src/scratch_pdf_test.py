from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPageSize, QPageLayout, QTextDocument
from PySide6.QtCore import Qt, QRectF, QMarginsF
from PySide6.QtPrintSupport import QPrinter

app = QApplication([])

printer = QPrinter(QPrinter.HighResolution)
printer.setOutputFormat(QPrinter.PdfFormat)
printer.setOutputFileName("test_table.pdf")

page_layout = QPageLayout()
page_layout.setPageSize(QPageSize(QPageSize.A4))
page_layout.setOrientation(QPageLayout.Portrait)
page_layout.setMargins(QMarginsF(0, 0, 0, 0))
printer.setPageLayout(page_layout)

painter = QPainter(printer)
dpcm = printer.resolution() / 2.54

html = """
<html>
<body>
<table border="1" width="100%">
<tr><th>Col 1</th><th>Col 2</th></tr>
<tr><td>Val 1</td><td>Val 2</td></tr>
</table>
</body>
</html>
"""

table_w = 18.0 * dpcm
scale = printer.resolution() / 96.0

doc = QTextDocument()
doc.setHtml(html)
doc.setTextWidth(table_w / scale)

painter.translate(1.5 * dpcm, 5.0 * dpcm)
painter.save()
painter.scale(scale, scale)
doc.drawContents(painter)
painter.restore()

painter.end()
print("Done")
