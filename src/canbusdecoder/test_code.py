import unittest
from unittest.mock import patch






from stats import show_stats
from decoder import parse_canID, convert_serializable, generate_output, decode



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

class TestShowStats(unittest.TestCase):
    def test_show_stats(self):
        decoded_lines = [
            {"unix_epoch": "100", "CanID": "BRAKE", "signal": {"pressure": 2.0}},
            {"unix_epoch": "102", "CanID": "BRAKE", "signal": {"pressure": 4.0}},
        ]

        with patch('builtins.print') as mock_print:
            show_stats(decoded_lines, diffpriv=False)
            mock_print.assert_any_call("Statistics: ")
            mock_print.assert_any_call("\t# of signals: 2")
            mock_print.assert_any_call("time between first and last signal: 2.0s")
            mock_print.assert_any_call("signals/sec: 1.0")
            mock_print.assert_any_call("BRAKE.pressure: 1.414214")



if __name__ == '__main__':
    unittest.main()