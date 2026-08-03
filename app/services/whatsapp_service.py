import re
from datetime import date
from urllib.parse import quote

from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

DIAS_SEMANA = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

CODIGO_PAIS_DEFECTO = "57"

class TelefonoInvalidoError(Exception):
    pass

def limpiar_telefono(telefono: str) -> str:
    """
    Limpia el numero de espacios, guiones, parentesis y el '+'.
    Antepone el código de pais de Colombia si no está ya presente.
    """
    if not telefono or not telefono.strip():
        raise TelefonoInvalidoError("El paciente no tiene teléfono registrado")

    limpio = re.sub(r"[\s\-\(\)\+]", "", telefono.strip())

    if not limpio.isdigit():
        raise TelefonoInvalidoError(
            f"El teléfono: '{telefono}' contiene caracteres no válidos"
        )
    
    if not limpio.startswith(CODIGO_PAIS_DEFECTO):
        limpio = CODIGO_PAIS_DEFECTO + limpio

    return limpio

def obtener_dia_semana(fecha: date) -> str:
    return DIAS_SEMANA[fecha.weekday()]

def _abrir_whatsapp(telefono: str, mensaje: str) -> None:
    telefono_limpio = limpiar_telefono(telefono)
    mensaje_codificado = quote(mensaje)
    url = f"https://wa.me/{telefono_limpio}?text={mensaje_codificado}"
    QDesktopServices.openUrl(QUrl(url))

def enviar_bienvenida (telefono: str, nombre_paciente: str, nombre_lab: str) -> None:
    mensaje = (
        f"Hola {nombre_paciente}, {nombre_lab} te da la bienvenida. "
        f"Esperemos que tu experiencia sea la mejor."
    )
    _abrir_whatsapp(telefono, mensaje)

def enviar_cita_asignada(
    telefono: str, nombre_paciente: str, nombre_lab: str,
    fecha: date, hora_str: str, localidad: str
) -> None:
    dia = obtener_dia_semana(fecha)
    fecha_str = fecha.strftime("%d/%m/%Y")
    mensaje = (
        f"Hola {nombre_paciente}, Tu cita con {nombre_lab} está asignada así: "
        f"El día {dia}, {fecha_str} - {hora_str} en la dirección {localidad}, Te esperamos"
    )
    _abrir_whatsapp(telefono, mensaje)


def enviar_confirmar_cita(
    telefono: str, nombre_paciente: str, nombre_lab: str,
    fecha: date, hora_str: str, localidad: str
) -> None:
    dia = obtener_dia_semana(fecha)
    fecha_str = fecha.strftime("%d/%m/%Y")
    mensaje = (
        f"Hola {nombre_paciente}, Tu cita con {nombre_lab} está asignada así: "
        f"El día {dia}, {fecha_str} - {hora_str} en la dirección {localidad}, "
        f"¿Confirmas tu asistencia?"
    )
    _abrir_whatsapp(telefono, mensaje)
