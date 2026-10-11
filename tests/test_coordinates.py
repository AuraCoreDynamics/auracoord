import unittest
from auracoord.converter import (
    latlon_to_dms,
    latlon_to_ddm,
    latlon_to_utm,
    latlon_to_mgrs,
    parse_any_coordinate,
)


class TestCoordinates(unittest.TestCase):
    def test_latlon_to_dms_washington_dc(self):
        dms = latlon_to_dms(38.8895, -77.0353)
        self.assertIn("38°53'", dms)
        self.assertIn("N", dms)
        self.assertIn("077°02'", dms)
        self.assertIn("W", dms)

    def test_latlon_to_ddm(self):
        ddm = latlon_to_ddm(38.8895, -77.0353)
        self.assertIn("38°53.370'N", ddm)
        self.assertIn("077°02.118'W", ddm)

    def test_latlon_to_utm(self):
        zone, hem, easting, northing = latlon_to_utm(38.8895, -77.0353)
        self.assertEqual(zone, 18)
        self.assertEqual(hem, "N")
        self.assertTrue(300000.0 < easting < 400000.0)
        self.assertTrue(4000000.0 < northing < 5000000.0)

    def test_latlon_to_mgrs(self):
        mgrs = latlon_to_mgrs(38.8895, -77.0353, precision=5)
        self.assertTrue(mgrs.startswith("18S"))
        self.assertTrue(len(mgrs) >= 13)

    def test_parse_any_coordinate_decimal(self):
        res = parse_any_coordinate("38.8895, -77.0353")
        self.assertIsNotNone(res)
        self.assertEqual(res["detectedFormat"], "DecimalDegrees")
        self.assertEqual(res["latitude"], 38.8895)
        self.assertEqual(res["longitude"], -77.0353)

    def test_parse_any_coordinate_dms(self):
        res = parse_any_coordinate("38°53'22.2\"N 77°02'07.1\"W")
        self.assertIsNotNone(res)
        self.assertEqual(res["detectedFormat"], "DegreesMinutesSeconds")
        self.assertAlmostEqual(res["latitude"], 38.8895, places=3)
        self.assertAlmostEqual(res["longitude"], -77.0353, places=3)

    def test_parse_any_coordinate_mgrs(self):
        res = parse_any_coordinate("18SUJ2345067890")
        self.assertIsNotNone(res)
        self.assertEqual(res["detectedFormat"], "MGRS")
        self.assertEqual(res["mgrs"], "18SUJ2345067890")


if __name__ == "__main__":
    unittest.main()
