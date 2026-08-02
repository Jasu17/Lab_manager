import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

SERVICIO_FIJO = "Laboratorio Clínico (Apoyo diagnóstico y complementación terapéutica)"

def calcular_edad (fecha_nacimiento: date | None) -> int | None:
    if fecha_nacimiento is None:
        return None

    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

def _dibujar_encabezado_pie(canvas, doc, datos: dict):
    canvas.saveState()
    ancho, alto = letter

    canvas.setFont("Helvetica", 9)
    canvas.drawString(2 * cm, alto - 1.5 * cm, datos.get("fecha_actual", ""))
    canvas.drawString(2 * cm, alto - 1.5 * cm - 0.35 * cm, datos.get("hora_actual", ""))

    texto_derecha = f"{datos.get('numero_cita', '')} - {datos.get('paciente_nombre', '')}"
    canvas.drawRightString(ancho - 2 * cm, alto - 1.5 * cm, texto_derecha)
    canvas.drawRightString(ancho - 2 * cm, alto - 1.5 * cm - 0.35 * cm, datos.get("fecha_cita", ""))

    canvas.drawCentredString(ancho / 2, 1.2 * cm, str(doc.page))
    canvas.restoreState()

def generar_pdf_resultado(ruta_archivo: str, datos: dict) -> str:
    """
    Genera el PDF de resultado con membrete institucional.

    datos: diccionario con las claves:
        numero_cita, fecha_cita, fecha_actual, hora_actual,
        paciente_nombre, paciente_documento, paciente_edad, paciente_sexo,
        paciente_estado_civil, paciente_regimen, paciente_ciudad,
        paciente_telefono, paciente_nacimiento,
        examen_nombre, resultado, referencia, fecha_examen,
        lab_nombre, lab_direccion, lab_ciudad, lab_logo_path,
        bacteriologa_nombre, bacteriologa_registro, bacteriologa_firma_path
    """

    doc = SimpleDocTemplate(
        ruta_archivo, pagesize=letter,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=3 * cm, bottomMargin=2.5 * cm
    )
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    small = ParagraphStyle("small", parent=normal, fontSize=9)
    titulo = ParagraphStyle("titulo", parent=normal, fontSize=14, fontName="Helvetica-Bold")
    seccion = ParagraphStyle("seccion", parent=normal, fontSize=12, fontName="Helvetica-Bold")
    nombre_examen_style = ParagraphStyle("nombre_examen", parent=normal, fontSize=13, fontName="Helvetica-Bold")
    centrado = ParagraphStyle("centrado", parent=normal, alignment=1)
    centrado_small = ParagraphStyle("centrado_small", parent=small, alignment=1)

    story = []

    # --- Encabezado institucional: datos del lab + logo ---
    lab_info = [
        Paragraph(datos.get("lab_nombre", ""), titulo),
        Spacer(1, 0.2 * cm),
        Paragraph(datos.get("lab_direccion") or "", normal),
        Paragraph(datos.get("lab_ciudad") or "", normal),
        Spacer(1, 0.3 * cm),
        Paragraph("<b>Bacterióloga Responsable</b>", normal),
        Paragraph(datos.get("bacteriologa_nombre") or "", normal),
    ]
    if datos.get("bacteriologa_registro"):
        lab_info.append(Paragraph(f"Registro Profesional: {datos['bacteriologa_registro']}", small))

    logo_path = datos.get("lab_logo_path")
    if logo_path and os.path.exists(logo_path):
        logo_cell = Image(logo_path, width=3 * cm, height=3 * cm)
    else:
        logo_cell = Paragraph("", normal)

    header_table = Table([[lab_info, logo_cell]], colWidths=[11 * cm, 4 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Table([[""]], colWidths=[17 * cm],
                        style=TableStyle([("LINEBELOW", (0, 0), (-1, -1), 1, colors.black)])))
    story.append(Spacer(1, 0.5 * cm))

    # --- Título "Historia clínica" ---
    titulo_hc = Table([[Paragraph("HISTORIA CLÍNICA", centrado)]], colWidths=[17 * cm])
    titulo_hc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(titulo_hc)
    story.append(Spacer(1, 0.4 * cm))

    # --- Datos del paciente ---
    edad = datos.get("paciente_edad")
    edad_str = f"{edad} años" if edad is not None else "N/A"

    filas_paciente = [
        [Paragraph(f"<b>Nombre:</b> {datos.get('paciente_nombre', '')}", normal),
         Paragraph(f"<b>Edad:</b> {edad_str}", normal)],
        [Paragraph(f"<b>Documento:</b> {datos.get('paciente_documento', '')}", normal),
         Paragraph(f"<b>Sexo:</b> {datos.get('paciente_sexo') or 'N/A'}", normal)],
        [Paragraph(f"<b>Estado civil:</b> {datos.get('paciente_estado_civil') or 'N/A'}", normal), ""],
        [Paragraph(f"<b>Nacimiento:</b> {datos.get('paciente_nacimiento') or 'N/A'}", normal),
         Paragraph(f"<b>Ciudad:</b> {datos.get('paciente_ciudad') or 'N/A'}", normal)],
        [Paragraph(f"<b>Teléfono:</b> {datos.get('paciente_telefono') or 'N/A'}", normal),
         Paragraph(f"<b>Fecha examen:</b> {datos.get('fecha_examen', '')}", normal)],
    ]
    tabla_paciente = Table(filas_paciente, colWidths=[8.5 * cm, 8.5 * cm])
    tabla_paciente.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tabla_paciente)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"<b>Examen solicitado:</b> {datos.get('examen_nombre', '')}", normal))
    story.append(Spacer(1, 0.6 * cm))

    # --- Sección de laboratorio (resultado, referencia, servicio) ---
    story.append(Paragraph("LABORATORIO", seccion))
    story.append(Spacer(1, 0.2 * cm))

    contenido_examen = [
        Paragraph(datos.get("examen_nombre", ""), nombre_examen_style),
        Spacer(1, 0.2 * cm),
        Paragraph("<b>Resultado</b>", normal),
        Paragraph(datos.get("resultado") or "Sin resultado registrado", normal),
        Spacer(1, 0.2 * cm),
        Paragraph("<b>Valor de referencia</b>", normal),
        Paragraph(datos.get("referencia") or "N/A", normal),
        Spacer(1, 0.2 * cm),
        Paragraph("<b>Servicio</b>", normal),
        Paragraph(SERVICIO_FIJO, normal),
    ]
    tabla_examen = Table([[contenido_examen]], colWidths=[17 * cm])
    tabla_examen.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(tabla_examen)
    story.append(Spacer(1, 1 * cm))

    # --- Firma (opcional) ---
    firma_path = datos.get("bacteriologa_firma_path")
    firma_elementos = []
    if firma_path and os.path.exists(firma_path):
        firma_elementos.append(Image(firma_path, width=5 * cm, height=2.5 * cm, hAlign="CENTER"))
    else:
        firma_elementos.append(Spacer(1, 1.5 * cm))

    firma_elementos.append(Table([[""]], colWidths=[7 * cm],
                                  style=TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.black)])))
    firma_elementos.append(Paragraph(f"<b>{datos.get('bacteriologa_nombre', '')}</b>", centrado))
    firma_elementos.append(Paragraph("Bacterióloga", centrado_small))
    if datos.get("bacteriologa_registro"):
        firma_elementos.append(Paragraph(f"Registro Profesional No. {datos['bacteriologa_registro']}", centrado_small))

    tabla_firma = Table([[firma_elementos]], colWidths=[17 * cm])
    tabla_firma.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(tabla_firma)

    def _on_page(canvas, doc_):
        _dibujar_encabezado_pie(canvas, doc_, datos)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return ruta_archivo