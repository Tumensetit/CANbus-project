import unittest
from unittest.mock import patch
from canbusdecoder.stats import calculate_stats
from canbusdecoder.decoder import parse_canID, convert_serializable, generate_output, decode

from copy import deepcopy

import cantools
import pytest


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


import os
import unittest

class TestDecodeFunctionWithSmallInputFile(unittest.TestCase):
    def test_decode_output(self):

        db = cantools.database.load_file("data/toyota_rav4_hybrid_2017_pt_generated.dbc")
        input_file = "tests/testinput_10_lines.tsv"
        output_file = "tests/test_output_file.json"
        query = "BRAKE"
        vss = False
        diffpriv = False

        stats, metadata = decode(db, input_file, output_file, query, vss, diffpriv)

        # Test input has 2 "BRAKE" messages + 1 one header
        self.assertEqual(len(stats), 3)
        self.assertEqual(metadata.message_count, 2)
        self.assertEqual(metadata.first_epoch, 1736342840.2959864)
        self.assertEqual(metadata.last_epoch, 1736342840.296327)

        if os.path.exists(output_file):
            os.remove(output_file)




if __name__ == '__main__':
    unittest.main()

