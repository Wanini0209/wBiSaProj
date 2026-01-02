import os
import pickle
from pathlib import Path
from typing import Any

import pytest

from wutils.io import pickle_dump, pickle_load


@pytest.mark.unit
class TestPickleIO:
    """Test suite for pickle-io."""

    # --- Custom Fixtures ---

    @pytest.fixture
    def sample_dict(self) -> dict[str, Any]:
        """Provide standard dictionary data for testing."""
        return {"key": "value", "num": 123}

    @pytest.fixture
    def complex_data(self) -> dict[str, Any]:
        """Provide nested structure data for Round-Trip testing."""
        return {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (10, 20),
            "set": {1, 2, 3},
        }

    # --- Happy Path Tests ---

    def test_tc_dump_happy_001_basic_str_path(
        self, tmp_path: Path, sample_dict: dict[str, Any]
    ) -> None:
        """TC-DUMP-HAPPY-001: Basic string path write.

        Test Target: Verify that passing a string path correctly creates the file and
        writes data.
        Expected Result: The target path file exists, and file size is greater than 0.
        """
        # Arrange
        path_str = str(tmp_path / "test.pkl")

        # Act
        pickle_dump(sample_dict, path_str)

        # Assert
        assert os.path.exists(path_str)
        assert os.path.getsize(path_str) > 0

    def test_tc_dump_happy_002_path_obj_write(
        self, tmp_path: Path, sample_dict: dict[str, Any]
    ) -> None:
        """TC-DUMP-HAPPY-002: Path object write.

        Test Target: Verify that passing a pathlib.Path object behaves consistently
        with string paths.
        Expected Result: The target path file exists.
        """
        # Arrange
        path_obj = tmp_path / "test_path.pkl"

        # Act
        pickle_dump(sample_dict, path_obj)

        # Assert
        assert path_obj.exists()

    def test_tc_dump_happy_003_kwargs_protocol(
        self, tmp_path: Path, sample_dict: dict[str, Any]
    ) -> None:
        """TC-DUMP-HAPPY-003: Parameter passthrough (Protocol).

        Test Target: Verify kwargs are correctly passed to the underlying pickle.dump
        (specify protocol).
        Expected Result: File is successfully created.
        """
        # Arrange
        target_path = tmp_path / "proto3.pkl"
        protocol_ver = 3

        # Act
        pickle_dump(sample_dict, target_path, protocol=protocol_ver)

        # Assert
        assert target_path.exists()
        # Verify validity by loading it back (implicit check that the format is valid)
        with open(target_path, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == sample_dict

    def test_tc_load_happy_001_basic_read(
        self, tmp_path: Path, sample_dict: dict[str, Any]
    ) -> None:
        """TC-LOAD-HAPPY-001: Basic read restoration.

        Test Target: Verify that objects can be correctly read and restored from an
        existing file.
        Expected Result: result content matches sample_dict.
        """
        # Arrange
        file_path = tmp_path / "valid.pkl"
        with open(file_path, "wb") as f:
            pickle.dump(sample_dict, f)

        # Act
        result = pickle_load(file_path)

        # Assert
        assert result == sample_dict

    def test_tc_load_happy_002_kwargs_encoding(
        self, tmp_path: Path, sample_dict: dict[str, Any]
    ) -> None:
        """TC-LOAD-HAPPY-002: Parameter passthrough (Encoding).

        Test Target: Verify kwargs are correctly passed to the underlying pickle.load.
        Expected Result: Read process completes without error or behavior is affected
        by parameters.
        """
        # Arrange
        file_path = tmp_path / "encoding.pkl"
        with open(file_path, "wb") as f:
            pickle.dump(sample_dict, f)

        # Act
        # Using default encoding parameters which should work for standard types
        result = pickle_load(file_path, encoding="ASCII", errors="strict")

        # Assert
        assert result == sample_dict

    # --- Error Handling Tests ---

    def test_tc_dump_err_001_unpicklable(self, tmp_path: Path) -> None:
        """TC-DUMP-ERR-001: Write unpicklable object.

        Test Target: Verify writing an object that cannot be serialized raises
        pickle.PickleError or subclass.
        Expected Result: Raises pickle.PickleError, AttributeError, or TypeError.
        """

        # Arrange
        # Local functions are typically unpicklable
        def unpicklable_obj(x: Any) -> Any:
            return x

        path = tmp_path / "fail.pkl"

        # Act & Assert
        with pytest.raises((pickle.PickleError, AttributeError, TypeError)):
            pickle_dump(unpicklable_obj, path)

    def test_tc_load_err_001_file_not_found(self, tmp_path: Path) -> None:
        """TC-LOAD-ERR-001: Read non-existent file.

        Test Target: Verify reading a non-existent file raises FileNotFoundError.
        Expected Result: Raises FileNotFoundError.
        """
        # Arrange
        ghost_path = tmp_path / "ghost.pkl"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            pickle_load(ghost_path)

    # --- Integration Tests ---

    def test_tc_int_happy_001_round_trip(
        self, tmp_path: Path, complex_data: dict[str, Any]
    ) -> None:
        """TC-INT-HAPPY-001: Full read/write cycle (Round-Trip).

        Test Target: Verify object remains consistent after Dump and Load (End-to-End).
        Expected Result: result exactly matches complex_data.
        """
        # Arrange
        cycle_path = tmp_path / "cycle.pkl"

        # Act
        pickle_dump(complex_data, cycle_path)
        result = pickle_load(cycle_path)

        # Assert
        assert result == complex_data
