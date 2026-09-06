import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'main-v2.py'

spec = importlib.util.spec_from_file_location('main_v2', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestMainV2(unittest.TestCase):
    def test_default_csv_loads_and_uses_southern_seasons(self):
        df = module.cargar_datos(None)

        self.assertIsNotNone(df)
        self.assertIn('Fecha', df.columns)
        self.assertIn('Temperatura Mínima (°C)', df.columns)
        self.assertIn('Estación', df.columns)

        expected = {'Verano', 'Otoño', 'Invierno', 'Primavera'}
        self.assertTrue(expected.issubset(set(df['Estación'].unique())))


if __name__ == '__main__':
    unittest.main()
