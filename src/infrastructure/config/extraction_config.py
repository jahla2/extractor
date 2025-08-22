import os


class ExtractionConfiguration:
    def __init__(self):
        self.row_tolerance_y = self._get_environment_float("ROW_TOL_Y", 0.012)
        self.column_stretch = self._get_environment_float("COL_STRETCH", 0.90)
        self.header_padding_y = self._get_environment_float("HEADER_PAD_Y", 0.003)
    
    def _get_environment_float(self, key: str, default_value: float) -> float:
        value = os.getenv(key, "").strip()
        if not value:
            return default_value
        try:
            return float(value)
        except ValueError:
            return default_value