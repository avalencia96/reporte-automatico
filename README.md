# 📊 Generador automático de reportes

![DevOps](https://img.shields.io/badge/DevOps-anton·io-8B5CF6?style=flat-square)
![Automatización](https://img.shields.io/badge/Automatización-Python%20·%20Docker-0A0A0F?style=flat-square)

Convierte un archivo de datos (CSV) en un **reporte visual listo para enviar**, sin trabajo manual. Pensado para dejar de armar el mismo reporte cada semana: se ejecuta solo (por ejemplo con `cron`) y puede mandar el resultado por correo automáticamente.

> Ejemplo real de automatización que ofrezco como servicio freelance. Si necesitas automatizar un reporte con tus propios datos, escríbeme.

---

## ✨ Qué hace

- Lee los datos desde un CSV (ventas, operaciones, métricas, lo que sea).
- Calcula indicadores clave: total, número de operaciones, ticket promedio, unidades, producto estrella.
- Genera un **gráfico** de ventas por producto.
- Produce un **reporte HTML autocontenido** (un solo archivo, gráfico incluido) listo para abrir o enviar.
- Opcionalmente lo **envía por correo** de forma automática.

---

## 🖼️ Resultado

El script genera un `reporte.html` como este:

- Tarjetas con las métricas principales.
- Gráfico de barras por producto.
- Tabla de detalle.
- Fecha de generación automática.

*(Abre `reporte.html` en el navegador para ver el ejemplo incluido.)*

---

## 🚀 Uso

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Genera el reporte con los datos de ejemplo:

```bash
python generar_reporte.py --datos ventas.csv --salida reporte.html
```

Genera **y envía por correo** automáticamente:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_USER=tu_correo@gmail.com
export SMTP_PASSWORD=tu_app_password
python generar_reporte.py --datos ventas.csv --salida reporte.html --enviar --destino cliente@ejemplo.com
```

> 🔒 Las credenciales se leen desde variables de entorno, **nunca** se escriben en el código.

---

## ⏰ Automatización con cron (opcional)

Para que corra solo cada lunes a las 8:00 AM y envíe el reporte:

```cron
0 8 * * 1 cd /ruta/al/proyecto && /usr/bin/python3 generar_reporte.py --datos ventas.csv --enviar --destino cliente@ejemplo.com
```

Y listo: el reporte llega al correo sin que nadie mueva un dedo.

---

## 📂 Formato de datos esperado

El CSV debe tener estas columnas:

| Columna    | Descripción                     |
|------------|---------------------------------|
| `fecha`    | Fecha de la operación (YYYY-MM-DD) |
| `producto` | Nombre del producto/servicio    |
| `cantidad` | Unidades vendidas               |
| `monto`    | Importe de la operación         |

Se adapta fácilmente a otras columnas o fuentes de datos (Excel, base de datos, API).

---

## 🛠️ Tecnologías

Python · pandas · matplotlib · SMTP

---

## 👤 Autor

**Antonio Valencia** — DevOps & Automatización
Automatizo reportes y tareas repetitivas, optimizo Docker/Linux y monto monitoreo.

---
<p align="center">
  <sub>Hecho por <b>anton·io</b> · DevOps &amp; Automatización · <a href="https://github.com/avalencia96">github.com/avalencia96</a></sub>
</p>
