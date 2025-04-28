import unittest
from unittest.mock import patch
from canbusdecoder.stats import show_stats
from canbusdecoder.decoder import parse_canID, convert_serializable, generate_output, decode



class TestParseCanID(unittest.TestCase):
    

    def test_valid_id(self):
        """Test that a valid CAN ID is correctly parsed and returned as an integer."""
        self.assertEqual(parse_canID("Ext. ID: 1234"), 1234)

    def test_missing_id(self):
        """Test that when there's no CAN ID in the string, None is returned."""
        self.assertIsNone(parse_canID("Some unrelated text"))

    def test_non_numeric_id(self):
        """Test that if the CAN ID is non-numeric, None is returned."""
        self.assertIsNone(parse_canID("Ext. ID: abc"))


class TestGenerateOutput(unittest.TestCase):

    def test_generate_output_without_vss(self):
        """Test generate_output without VSS mapping."""
        timestamp = "1234567890"
        canID = "BRAKE"
        data = {"signal1": 1, "signal2": 2}
        expected = {
            "unix_epoch": timestamp,
            "CanID": canID,
            "signal": {"signal1": 1, "signal2": 2}
        }
        output = generate_output(timestamp, canID, data, vss=False)
        self.assertEqual(output, expected)

    def test_generate_output_with_vss(self):
        """Test generate_output with VSS mapping for known signals."""
        timestamp = "1234567890"
        canID = "BRAKE"
        data = {"SPEED": 55, "signal2": 2}
        expected = {
            "unix_epoch": timestamp,
            "CanID": canID,
            "signal": {
                "Vehicle.Speed": 55,  
                "signal2": 2          
            }
        }
        output = generate_output(timestamp, canID, data, vss=True)
        self.assertEqual(output, expected)

if __name__ == '__main__':
    unittest.main()
