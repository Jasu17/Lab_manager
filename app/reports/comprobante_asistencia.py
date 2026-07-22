from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

def generar_pdf_comprobante_asistencia(ruta_archivo: str, cita: dict) -> str:
    """
    Genera un reporte en PDF de asistencia.

    cita: Diccionario con las claves:
        - nombre del paciente, identificacion y tipo de id
        - fecha y hora,
        - Localidad

    Retorna la ruta del archivo generado.
    """

    c = canvas.Canvas(ruta_archivo, pagesize=letter)
    ancho, alto = letter

    y = alto - 3 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Comprobande de Asistencia")
    y -= 1.5 * cm

    c.setFont("Helvetica", 11)

    campos = [
        ("Paciente:", cita["paciente_nombre"]),
        ("Identificación:", f"{cita['paciente_tipo_id']} {cita['paciente_identificacion']}"),
        ("Fecha:", cita["fecha"]),
        ("Hora:", cita["hora"]),
        ("Localidad:", cita["localidad"] or "N/A"),
    ]

    for etiqueta, valor in campos:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, etiqueta)
        c.setFont("Helvetica", 11)
        c.drawString(6 * cm, y, str(valor))
        y -= 0.8 * cm

    y -= 1 * cm
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(2 * cm, y, "Este documento certifica la asistencia del paciente a la cita programada")

    c.showPage()
    c.save()
    return ruta_archivo