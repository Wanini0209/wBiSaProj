import json
from pathlib import Path
from typing import Any

import pytest

# === System Under Test (SUT) ===
from wutils.io import json_dump, json_load


@pytest.mark.unit
class TestJsonIO:
    """Test suite for json-io."""

    # --- Custom Fixtures ---

    @pytest.fixture
    def sample_data(self) -> dict[str, Any]:
        """Provide standard test data with Chinese characters and nested structure."""
        return {
            "name": "測試",
            "value": 100,
            "nested": {"active": True, "list": [1, 2, 3]},
        }

    # === json_dump Tests ===

    def test_tc_dump_happy_001_utf8_encoding(self, tmp_path, sample_data):
        """TC-DUMP-HAPPY-001: Force UTF-8 writing.

        Test Objective: Verify that writing data containing non-ASCII (e.g., Chinese)
        creates the file in UTF-8.
        Expected Result: File created successfully, content can be decoded as UTF-8
        and contains expected Chinese characters.
        """
        # Arrange
        file_path = tmp_path / "utf8.json"

        # Act
        json_dump(sample_data, file_path)

        # Assert
        # Verify content is readable as UTF-8 and matches expected JSON structure
        # without escaping ASCII
        content = file_path.read_text(encoding="utf-8")
        expected_json = json.dumps(sample_data, ensure_ascii=False)
        assert content == expected_json

    def test_tc_dump_happy_002_str_path(self, tmp_path):
        """TC-DUMP-HAPPY-002: Support string paths.

        Test Objective: Verify json_dump accepts str type path arguments.
        Expected Result: Function executes successfully and file exists at the
        specified path.
        """
        # Arrange
        data = {"k": "v"}
        str_path = str(tmp_path / "str_path.json")

        # Act
        json_dump(data, str_path)

        # Assert
        assert Path(str_path).exists()

    def test_tc_dump_happy_003_indent_passthrough(self, tmp_path):
        r"""TC-DUMP-HAPPY-003: Parameter passthrough (Indent).

        Test Objective: Verify kwargs (like indent) are correctly passed to the
        underlying json.dump.
        Expected Result: Generated file content contains newlines \n and indentation
        spaces.
        """
        # Arrange
        data = {"a": 1, "b": 2}
        file_path = tmp_path / "indent.json"

        # Act
        json_dump(data, file_path, indent=4)

        # Assert
        file_content = file_path.read_text(encoding="utf-8")
        assert "\n    " in file_content

    def test_tc_dump_err_001_unserializable(self, tmp_path):
        """TC-DUMP-ERR-001: Unserializable object.

        Test Objective: Verify that passing an unserializable object (like set) passes
        through the underlying TypeError.
        Expected Result: Raises TypeError.
        """
        # Arrange
        data = {"s": {1, 2}}  # Sets are not JSON serializable by default
        file_path = tmp_path / "error.json"

        # Act & Assert
        with pytest.raises(TypeError):
            json_dump(data, file_path)

    # === json_load Tests ===

    def test_tc_load_happy_001_utf8_read(self, tmp_path, sample_data):
        """TC-LOAD-HAPPY-001: Force UTF-8 reading.

        Test Objective: Verify correct reading of UTF-8 encoded JSON files containing
        Chinese characters.
        Expected Result: loaded_data matches original data consistent with UTF-8
        decoding.
        """
        # Arrange
        file_path = tmp_path / "utf8_read.json"
        # Write UTF-8 data manually
        file_path.write_text(
            json.dumps(sample_data, ensure_ascii=False), encoding="utf-8"
        )

        # Act
        loaded_data = json_load(file_path)

        # Assert
        assert loaded_data == sample_data

    def test_tc_load_happy_002_str_path(self, tmp_path):
        """TC-LOAD-HAPPY-002: Support string paths.

        Test Objective: Verify json_load accepts str type path arguments.
        Expected Result: Successfully reads and returns data.
        """
        # Arrange
        data = {"test": "str_path"}
        file_path = tmp_path / "read_str.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        # Act
        result = json_load(str(file_path))

        # Assert
        assert result == data

    def test_tc_load_err_001_file_not_found(self, tmp_path):
        """TC-LOAD-ERR-001: File not found.

        Test Objective: Verify that reading a non-existent file passes through
        FileNotFoundError.
        Expected Result: Raises FileNotFoundError.
        """
        # Arrange
        non_existent_path = tmp_path / "ghost.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            json_load(non_existent_path)

    def test_tc_load_err_002_invalid_json(self, tmp_path):
        """TC-LOAD-ERR-002: Invalid JSON format.

        Test Objective: Verify that reading an invalid JSON file passes through
        json.JSONDecodeError.
        Expected Result: Raises json.JSONDecodeError.
        """
        # Arrange
        invalid_file_path = tmp_path / "invalid.json"
        invalid_file_path.write_text("{invalid-json", encoding="utf-8")

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json_load(invalid_file_path)

    # === Integration Tests ===

    def test_tc_int_happy_001_round_trip(self, tmp_path, sample_data):
        """TC-INT-HAPPY-001: Complete Round-Trip.

        Test Objective: Verify that complex objects written by dump can be read back
        by load without error.
        Expected Result: result exactly equals sample_data.
        """
        # Arrange
        file_path = tmp_path / "round_trip.json"

        # Act
        json_dump(sample_data, file_path)
        result = json_load(file_path)

        # Assert
        assert result == sample_data
