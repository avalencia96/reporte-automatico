"""Genera portada.png (16:9) y reporte.pdf a partir de ventas.csv."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
from datetime import datetime

df = pd.read_csv("ventas.csv", parse_dates=["fecha"]).sort_values("fecha")
por_prod = df.groupby("producto")["monto"].sum().sort_values(ascending=False)
total = df["monto"].sum()
ops = len(df)
ticket = df["monto"].mean()
unid = int(df["cantidad"].sum())
top = por_prod.idxmax()

MOR = "#6c4cf1"
LILA = "#f4f1ff"

# ---------- PORTADA 1200x675 (16:9) ----------
fig = plt.figure(figsize=(12, 6.75), dpi=100)
fig.patch.set_facecolor("white")

# encabezado
fig.text(0.05, 0.88, "Automatización de reportes", fontsize=30, fontweight="bold", color=MOR)
fig.text(0.05, 0.81, "De un CSV a un reporte visual enviado por correo — sin trabajo manual",
         fontsize=13, color="#555")

# tarjetas de métricas
tarjetas = [("Ventas totales", f"${total:,.0f}"),
            ("Operaciones", f"{ops}"),
            ("Ticket promedio", f"${ticket:,.0f}"),
            ("Unidades", f"{unid}")]
x0, w, gap = 0.05, 0.205, 0.02
for i, (etq, val) in enumerate(tarjetas):
    x = x0 + i * (w + gap)
    ax = fig.add_axes([x, 0.55, w, 0.18])
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=LILA, edgecolor="none", transform=ax.transAxes))
    ax.text(0.5, 0.62, val, ha="center", va="center", fontsize=22, fontweight="bold",
            color=MOR, transform=ax.transAxes)
    ax.text(0.5, 0.25, etq, ha="center", va="center", fontsize=11, color="#555",
            transform=ax.transAxes)

# gráfico de barras
axb = fig.add_axes([0.05, 0.10, 0.60, 0.36])
por_prod.plot(kind="bar", ax=axb, color=MOR)
axb.set_title("Ventas por producto", fontsize=12, color="#333")
axb.set_xlabel("")
axb.set_ylabel("Monto ($)", fontsize=10)
plt.setp(axb.get_xticklabels(), rotation=20, ha="right", fontsize=9)

# panel derecho
axr = fig.add_axes([0.70, 0.10, 0.25, 0.36]); axr.axis("off")
axr.text(0, 0.9, "Producto estrella", fontsize=11, color="#777")
axr.text(0, 0.72, top, fontsize=18, fontweight="bold", color=MOR)
axr.text(0, 0.40, "Tecnologías", fontsize=11, color="#777")
axr.text(0, 0.25, "Python · pandas · matplotlib · SMTP", fontsize=10, color="#333")

fig.text(0.95, 0.03, "Antonio Valencia — DevOps & Automatización", fontsize=10,
         color="#999", ha="right")
fig.savefig("portada.png", facecolor="white")
plt.close(fig)

# ---------- gráfico para el PDF ----------
figc, axc = plt.subplots(figsize=(7, 3.2))
por_prod.plot(kind="bar", ax=axc, color=MOR)
axc.set_title("Ventas por producto")
axc.set_ylabel("Monto ($)"); axc.set_xlabel("")
plt.setp(axc.get_xticklabels(), rotation=20, ha="right")
plt.tight_layout()
figc.savefig("_chart.png", dpi=130)
plt.close(figc)

# ---------- PDF ----------
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=colors.HexColor(MOR))
sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=colors.grey, fontSize=9)

doc = SimpleDocTemplate("reporte.pdf", pagesize=LETTER,
                        topMargin=1.8*cm, bottomMargin=1.8*cm)
story = []
story.append(Paragraph("Reporte de ventas", h1))
story.append(Paragraph(f"Generado automáticamente el {datetime.now():%d/%m/%Y %H:%M}", sub))
story.append(Spacer(1, 14))

data = [["Ventas totales", "Operaciones", "Ticket promedio", "Unidades"],
        [f"${total:,.0f}", f"{ops}", f"${ticket:,.0f}", f"{unid}"]]
t = Table(data, colWidths=[4.2*cm]*4)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(LILA)),
    ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor(MOR)),
    ("FONTSIZE", (0, 1), (-1, 1), 15),
    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e6e0ff")),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
]))
story.append(t)
story.append(Spacer(1, 10))
story.append(Paragraph(f"<b>Producto estrella:</b> {top}", styles["Normal"]))
story.append(Spacer(1, 12))
story.append(Image("_chart.png", width=15*cm, height=6.85*cm))
story.append(Spacer(1, 8))

filas = [["Producto", "Monto"]] + [[p, f"${m:,.2f}"] for p, m in por_prod.items()]
td = Table(filas, colWidths=[10*cm, 5*cm])
td.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#faf9ff")),
    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#eeeeee")),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(td)
story.append(Spacer(1, 20))
story.append(Paragraph("Reporte automatizado · Antonio Valencia · DevOps & Automatización", sub))
doc.build(story)
print("OK portada.png y reporte.pdf")
