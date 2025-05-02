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

        metadata = decode(db, input_file, output_file, query, vss, diffpriv)

        # Test input has 2 "BRAKE" messages + 1 one header
        self.assertEqual(len(metadata.stats), 3)
        self.assertEqual(metadata.all_messages_count, 10)
        self.assertEqual(metadata.decoded_message_count, 2)
        self.assertEqual(metadata.first_epoch, 1736342840.2959864)
        self.assertEqual(metadata.last_epoch, 1736342840.296327)

        if os.path.exists(output_file):
            os.remove(output_file)


@pytest.fixture
def sample_data():
    return {
        "temperature": [22.5, 23.0, 21.8, 22.1, 22.7, 23.2, 22.9, 21.5, 22.0, 23.1],
        "humidity": [45.0, 47.2, 46.8, 44.1, 43.9, 45.3, 46.0, 44.7, 45.8, 46.5],
    }

def test_incremental_vs_full_batch(sample_data):
    # Arrange
    split_data = []
    for i in range(5):
        chunk = {}
        for key in sample_data:
            start = i * 2
            end = (i + 1) * 2
            chunk[key] = sample_data[key][start:end]
        split_data.append(chunk)

    # Act
    stats_full = calculate_stats([], dict(sample_data), diffpriv=False)

    stats_incremental = []
    for chunk in split_data:
        stats_incremental = calculate_stats(stats_incremental, chunk, diffpriv=False)

    # Assert
    stats_full_sorted = sorted(stats_full, key=lambda x: x[0])
    stats_incremental_sorted = sorted(stats_incremental, key=lambda x: x[0])

    assert len(stats_full_sorted) == len(stats_incremental_sorted)

    for full, inc in zip(stats_full_sorted, stats_incremental_sorted):
        assert full[0] == inc[0]  # key
        assert full[1] == inc[1]  # count
        assert full[2] == inc[2]  # min
        assert full[3] == inc[3]  # max
        assert pytest.approx(full[4], rel=1e-9) == inc[4]  # mean
        assert pytest.approx(full[5], rel=1e-9) == inc[5]  # stddev
        assert pytest.approx(full[6], rel=1e-9) == inc[6] # M2
        full_data = deepcopy(sample_data)

        split_data = []
        for i in range(5):
            chunk = {}
            for key in sample_data:
                start = i * 2
                end = (i + 1) * 2
                chunk[key] = sample_data[key][start:end]
            split_data.append(chunk)

        # Act
        stats_full = calculate_stats([], full_data, diffpriv=False)

        stats_incremental = []
        for chunk in split_data:
            stats_incremental = calculate_stats(stats_incremental, chunk, diffpriv=False)

        # Assert
        # Sort both lists by key name for consistent comparison
        stats_full_sorted = sorted(stats_full, key=lambda x: x[0])
        stats_incremental_sorted = sorted(stats_incremental, key=lambda x: x[0])

        assert len(stats_full_sorted) == len(stats_incremental_sorted)

        for full, inc in zip(stats_full_sorted, stats_incremental_sorted):
            assert full[0] == inc[0]  # key
            assert full[1] == inc[1]  # count
            assert full[2] == inc[2]  # min
            assert full[3] == inc[3]  # max
            assert pytest.approx(full[4], rel=1e-9) == inc[4]  # mean
            assert pytest.approx(full[5], rel=1e-9) == inc[5]  # stddev
            assert pytest.approx(full[6], rel=1e-9) == inc[6]  # M2




if __name__ == '__main__':
    unittest.main()

