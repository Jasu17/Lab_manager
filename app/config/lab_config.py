import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'lab_config.json')

DEFAULTS = {
    "nombre_lab": "Laboratorio Clínico",
    "direccion_lab":"",
    "ciudad_lab":"",
    "logo_path":"",
}

def get_lab_config() -> dict:
    """Lee la configuracion actual del laboratorio, o valores por defecto si no existen"""
    if not os.path.exists(CONFIG_PATH):
        return DEFAULTS.copy()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    config = DEFAULTS.copy()
    config.update(data)
    return config

def save_lab_config(config: dict) -> None:
    """Guarda la configuracion del laboratorio en el archivo JSON"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)