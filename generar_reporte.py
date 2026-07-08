#!/usr/bin/env python3
"""
Generador automático de reportes.

Lee un archivo de datos (CSV), calcula métricas clave, genera un gráfico
y produce un reporte en HTML. Opcionalmente lo envía por correo.

Pensado para correr solo (por ejemplo con cron) y dejar de armar el reporte
a mano cada semana.

Uso:
    python generar_reporte.py --datos ventas.csv --salida reporte.html
    python generar_reporte.py --datos ventas.csv --salida reporte.html --enviar

Autor: Antonio Valencia
"""

import argparse
import base64
import io
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib

matplotlib.use("Agg")  # backend sin ventana, ideal para servidores
import matplotlib.pyplot as plt
import pandas as pd


def cargar_datos(ruta):
    """Carga el CSV y valida que tenga las columnas mínimas esperadas."""
    if not os.path.exists(ruta):
        sys.exit(f"[ERROR] No se encontró el archivo de datos: {ruta}")

    df = pd.read_csv(ruta, parse_dates=["fecha"])
    columnas_requeridas = {"fecha", "producto", "cantidad", "monto"}
    faltantes = columnas_requeridas - set(df.columns)
    if faltantes:
        sys.exit(f"[ERROR] Faltan columnas en el CSV: {', '.join(faltantes)}")

    return df.sort_values("fecha")


def calcular_metricas(df):
    """Calcula los indicadores clave que verá el cliente en el reporte."""
    return {
        "total_ventas": df["monto"].sum(),
        "num_operaciones": len(df),
        "ticket_promedio": df["monto"].mean(),
        "unidades_vendidas": int(df["cantidad"].sum()),
        "producto_top": df.groupby("producto")["monto"].sum().idxmax(),
        "por_producto": df.groupby("producto")["monto"].sum().sort_values(ascending=False),
        "por_dia": df.groupby(df["fecha"].dt.date)["monto"].sum(),
    }


def generar_grafico(metricas):
    """Crea un gráfico de barras de ventas por producto y lo devuelve como
    imagen embebida en base64 (así el HTML es un solo archivo autocontenido)."""
    fig, ax = plt.subplots(figsize=(8, 4))
    metricas["por_producto"].plot(kind="bar", ax=ax, color="#6c4cf1")
    ax.set_title("Ventas por producto")
    ax.set_ylabel("Monto ($)")
    ax.set_xlabel("")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=110)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def construir_html(metricas, grafico_b64):
    """Arma el HTML del reporte con las métricas y el gráfico."""
    filas_productos = "".join(
        f"<tr><td>{producto}</td><td style='text-align:right'>${monto:,.2f}</td></tr>"
        for producto, monto in metricas["por_producto"].items()
    )
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Reporte de ventas</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; color: #222; max-width: 820px;
         margin: 24px auto; padding: 0 16px; }}
  h1 {{ color: #6c4cf1; margin-bottom: 4px; }}
  .sub {{ color: #777; margin-top: 0; font-size: 14px; }}
  .cards {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 24px 0; }}
  .card {{ flex: 1 1 160px; background: #f4f1ff; border-radius: 10px; padding: 16px; }}
  .card .valor {{ font-size: 24px; font-weight: bold; color: #6c4cf1; }}
  .card .etq {{ font-size: 13px; color: #555; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
  th, td {{ padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 14px; }}
  th {{ text-align: left; background: #faf9ff; }}
  img {{ width: 100%; border: 1px solid #eee; border-radius: 8px; margin-top: 12px; }}
  .pie {{ color: #999; font-size: 12px; margin-top: 32px; text-align: center; }}
</style>
</head>
<body>
  <h1>Reporte de ventas</h1>
  <p class="sub">Generado automáticamente el {fecha_generacion}</p>

  <div class="cards">
    <div class="card"><div class="valor">${metricas['total_ventas']:,.0f}</div>
      <div class="etq">Ventas totales</div></div>
    <div class="card"><div class="valor">{metricas['num_operaciones']}</div>
      <div class="etq">Operaciones</div></div>
    <div class="card"><div class="valor">${metricas['ticket_promedio']:,.0f}</div>
      <div class="etq">Ticket promedio</div></div>
    <div class="card"><div class="valor">{metricas['unidades_vendidas']}</div>
      <div class="etq">Unidades vendidas</div></div>
  </div>

  <p><strong>Producto estrella:</strong> {metricas['producto_top']}</p>

  <img src="data:image/png;base64,{grafico_b64}" alt="Ventas por producto">

  <h3>Detalle por producto</h3>
  <table>
    <tr><th>Producto</th><th style="text-align:right">Monto</th></tr>
    {filas_productos}
  </table>

  <p class="pie">Reporte automatizado · Antonio Valencia · DevOps &amp; Automatización</p>
</body>
</html>"""


def enviar_correo(html, destino):
    """Envía el reporte por correo usando credenciales SMTP tomadas de
    variables de entorno (nunca se escriben en el código)."""
    host = os.environ.get("SMTP_HOST")
    puerto = int(os.environ.get("SMTP_PORT", 587))
    usuario = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")

    if not all([host, usuario, password]):
        sys.exit("[ERROR] Falta configurar SMTP_HOST, SMTP_USER y SMTP_PASSWORD "
                 "como variables de entorno.")

    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = f"Reporte de ventas — {datetime.now():%d/%m/%Y}"
    mensaje["From"] = usuario
    mensaje["To"] = destino
    mensaje.attach(MIMEText(html, "html"))

    with smtplib.SMTP(host, puerto) as servidor:
        servidor.starttls()
        servidor.login(usuario, password)
        servidor.sendmail(usuario, destino, mensaje.as_string())

    print(f"[OK] Reporte enviado a {destino}")


def main():
    parser = argparse.ArgumentParser(description="Genera un reporte de ventas automático.")
    parser.add_argument("--datos", default="ventas.csv", help="Ruta del CSV de entrada")
    parser.add_argument("--salida", default="reporte.html", help="Ruta del HTML de salida")
    parser.add_argument("--enviar", action="store_true", help="Enviar el reporte por correo")
    parser.add_argument("--destino", help="Correo destino (si se usa --enviar)")
    args = parser.parse_args()

    df = cargar_datos(args.datos)
    metricas = calcular_metricas(df)
    grafico = generar_grafico(metricas)
    html = construir_html(metricas, grafico)

    with open(args.salida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Reporte generado: {args.salida}")

    if args.enviar:
        if not args.destino:
            sys.exit("[ERROR] Usa --destino correo@ejemplo.com junto con --enviar")
        enviar_correo(html, args.destino)


if __name__ == "__main__":
    main()
