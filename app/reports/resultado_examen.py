from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

def generar_pdf_resultado (ruta_archivo: str, examen: dict) -> str:
    """
    Genera un PDF con el resultado de un examen

    Examen: diccionario con las claves
        - nombre, identificacion, tipo ID
        - tipo examen
        - Resultado, observaciones
        - Fecha
        - Nombre del usuario que realizó el examen

    Retorna la ruta del archivo generado
    """

    c = canvas.Canvas(ruta_archivo, pagesize=letter)
    ancho, alto = letter

    y = alto - 3 *cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Resultado de Examen de Laboratorio")
    y -= 1.5 *cm

    c.setFont("Helvetica", 11)

    campos = [
        ("Paciente:", examen["paciente_nombre"]),
        ("Identificación:", f"{examen['paciente_tipo_id']} {examen['paciente_identificacion']}"),
        ("Tipo de examen:", examen["tipo_examen_nombre"]),
        ("Fecha:", examen["fecha"]),
        ("Realizado por:", examen["usuario_nombre"] or "N/A"),
    ]

    for etiqueta, valor in campos:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, etiqueta)
        c.setFont("Helvetica", 11)
        c.drawString(6 * cm, y, str(valor))
        y -= 0.6 * cm

    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Resultado:")
    y -= 0.8 * cm
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, examen["resultado"] or "Sin resultado registrado")

    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Observaciones:")
    y -= 0.8 * cm
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, examen["observaciones"] or "Sin observaciones")

    c.showPage()
    c.save()
    return ruta_archivo