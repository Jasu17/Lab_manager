from PySide6.QtCore import QTimer

class DebouncedSearch:
    def __init__(self, input_widget, callback, delay_ms: int=500, min_chars: int=3, ):
        self.callback = callback
        self.min_chars = min_chars

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(delay_ms)
        self.timer.timeout.connect(self._ejecutar_busqueda)

        self._texto_actual = ""
        input_widget.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, texto: str):
        self._texto_actual = texto.strip()
        if len(self._texto_actual) >= self.min_chars:
            self.timer.start()
        else:
            self.timer.stop()

    def _ejecutar_busqueda(self):
        self.callback(self._texto_actual)