"""Build fillable (AcroForm) invoice and receipt PDFs: every name, date, line item and total is an editable field."""

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

TEAL = HexColor("#0F766E")
INK = HexColor("#0F172A")
MUTED = HexColor("#64748B")
LINE = HexColor("#E2E8F0")
FIELD_BG = HexColor("#F8FAFC")
W, H = A4
M = 48  # page margin
ITEM_ROWS = 6


def field(c, name, x, y, w, h=18, value="", size=10, bold=False):
    c.acroForm.textfield(
        name=name, tooltip=name, x=x, y=y, width=w, height=h, value=value,
        fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size, borderWidth=0,
        fillColor=FIELD_BG, textColor=INK, forceBorder=False, annotationFlags="print",
    )


def header(c, title):
    c.drawImage("assets/logo.png", M, H - M - 48, width=180, height=48, mask="auto")
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 26)
    c.drawRightString(W - M, H - M - 30, title)
    c.setStrokeColor(LINE)
    c.line(M, H - M - 70, W - M, H - M - 70)


def label(c, text, x, y, size=8):
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text.upper())


def parties(c, top):
    label(c, "From", M, top)
    for i, (n, v) in enumerate([("from_name", "[Company name]"), ("from_address", "[Street, City, Country]"), ("from_contact", "[email] · [phone]")]):
        field(c, n, M, top - 22 - i * 20, 230, value=v)
    label(c, "Bill to", W / 2 + 10, top)
    for i, (n, v) in enumerate([("client_name", "[Client name]"), ("client_address", "[Client address]"), ("client_contact", "[Client email]")]):
        field(c, n, W / 2 + 10, top - 22 - i * 20, 230, value=v)


def meta(c, top, rows):
    x = W - M - 200
    for i, (lab, name, value) in enumerate(rows):
        y = top - i * 22
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(x, y + 5, lab)
        field(c, name, x + 80, y, 120, value=value)


def items_table(c, top):
    cols = [("Description", 260), ("Qty", 50), ("Unit price", 90), ("Amount", 99)]
    c.setFillColor(TEAL)
    c.rect(M, top, W - 2 * M, 22, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    x = M + 8
    for name, width in cols:
        c.drawString(x, top + 7, name.upper())
        x += width
    y = top
    for r in range(ITEM_ROWS):
        y -= 24
        x = M + 4
        for (name, width), key in zip(cols, ("desc", "qty", "price", "amount")):
            field(c, f"item{r + 1}_{key}", x, y + 3, width - 8, value="")
            x += width
        c.setStrokeColor(LINE)
        c.line(M, y, W - M, y)
    return y


def totals(c, top, rows):
    x = W - M - 220
    for i, (lab, name, bold) in enumerate(rows):
        y = top - 26 - i * 24
        c.setFillColor(INK if bold else MUTED)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 11 if bold else 10)
        c.drawString(x, y + 5, lab)
        field(c, name, x + 110, y, 110, value="", size=11 if bold else 10, bold=bold)
    return top - 26 - len(rows) * 24


def notes(c, top, text_label, value):
    label(c, text_label, M, top)
    c.acroForm.textfield(name="notes", x=M, y=top - 70, width=W - 2 * M, height=60, value=value, fontName="Helvetica",
                         fontSize=9, borderWidth=0, fillColor=FIELD_BG, textColor=INK, fieldFlags="multiline")


def footer(c):
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 30, "[Company name] · [Registration / VAT number] · [domain.com]")


def invoice(path="pdf/invoice-editable.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Invoice - editable template")
    header(c, "INVOICE")
    parties(c, H - M - 100)
    meta(c, H - M - 190, [("Invoice #", "invoice_number", "[INV-0001]"), ("Issue date", "issue_date", "[DD.MM.YYYY]"), ("Due date", "due_date", "[DD.MM.YYYY]")])
    bottom = items_table(c, H - M - 290)
    end = totals(c, bottom, [("Subtotal", "subtotal", False), ("Tax", "tax", False), ("Total due", "total", True)])
    notes(c, end - 20, "Payment details", "[Bank / IBAN / wallet] · Please include the invoice number as reference.")
    footer(c)
    c.save()


def receipt(path="pdf/receipt-editable.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Receipt - editable template")
    header(c, "RECEIPT")
    parties(c, H - M - 100)
    meta(c, H - M - 190, [("Receipt #", "receipt_number", "[RC-0001]"), ("Paid on", "paid_date", "[DD.MM.YYYY]"), ("Method", "payment_method", "[Card / Transfer]")])
    bottom = items_table(c, H - M - 290)
    end = totals(c, bottom, [("Subtotal", "subtotal", False), ("Tax", "tax", False), ("Amount paid", "total", True)])
    c.setFillColor(TEAL)
    c.roundRect(M, end - 46, 120, 30, 6, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(M + 60, end - 36, "PAID")
    notes(c, end - 70, "Notes", "Thank you for your business.")
    footer(c)
    c.save()


if __name__ == "__main__":
    invoice()
    receipt()
    print("ok")
