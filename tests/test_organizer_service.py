"""Tests for Organizer MCP Server."""

import pytest
import tempfile
from pathlib import Path
from services.organizer_service import OrganizerService
from services.file_operations_service import FileOperationsService


@pytest.fixture
def temp_folder():
    """Create a temporary folder for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def organizer_service():
    """Create an OrganizerService instance."""
    return OrganizerService()


@pytest.fixture
def file_operations_service():
    """Create a FileOperationsService instance."""
    return FileOperationsService()


class TestFileOperationsService:
    """Tests for FileOperationsService."""

    def test_read_file(self, file_operations_service, temp_folder):
        """Test reading a text file."""
        test_file = temp_folder / "test.txt"
        test_file.write_text("Hello, World!")

        result = file_operations_service.read_file(str(test_file))

        assert result.ok
        assert result.data["file_info"]["file_name"] == "test.txt"
        assert "Hello, World!" in result.data["file_info"]["content"]

    def test_read_nonexistent_file(self, file_operations_service):
        """Test reading a file that doesn't exist."""
        result = file_operations_service.read_file("/nonexistent/file.txt")

        assert not result.ok
        assert result.error.code == "file_access_error"

    def test_rename_file(self, file_operations_service, temp_folder):
        """Test renaming a file."""
        test_file = temp_folder / "old_name.txt"
        test_file.write_text("content")

        result = file_operations_service.rename_file(str(test_file), "new_name.txt")

        assert result.ok
        assert result.data["rename_info"]["new_name"] == "new_name.txt"
        assert (temp_folder / "new_name.txt").exists()

    def test_create_junk_folder(self, file_operations_service, temp_folder):
        """Test creating junk folder and moving files."""
        file1 = temp_folder / "file1.txt"
        file2 = temp_folder / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        result = file_operations_service.create_junk_folder(
            str(temp_folder),
            [str(file1), str(file2)],
            "_junk"
        )

        assert result.ok
        assert result.data["junk_result"]["files_moved"] == 2
        assert (temp_folder / "_junk").exists()
        assert (temp_folder / "_junk" / "file1.txt").exists()


class TestOrganizerService:
    """Tests for OrganizerService."""

    def test_find_duplicates(self, organizer_service, temp_folder):
        """Test finding duplicate files."""
        # Create two identical files
        file1 = temp_folder / "file1.txt"
        file2 = temp_folder / "file2.txt"
        content = "identical content"
        file1.write_text(content)
        file2.write_text(content)

        result = organizer_service.find_duplicates(str(temp_folder))

        assert result.ok
        assert result.data["duplicates"]["total_files"] == 2

    def test_suggest_filename(self, organizer_service, temp_folder):
        """Test filename suggestions."""
        test_file = temp_folder / "untitled.txt"
        test_file.write_text("This is a project charter for Project Alpha")

        result = organizer_service.suggest_filename(str(test_file))

        assert result.ok
        suggestions = result.data["suggestion"]["suggested_names"]
        assert len(suggestions) > 0
        # Should suggest something related to content

    def test_organize_files(self, organizer_service, temp_folder):
        """Test organizing files."""
        file1 = temp_folder / "financial_report.pdf"
        file2 = temp_folder / "vacation_photo.jpg"
        file1.write_text("PDF content")
        file2.write_text("JPG content")

        organization_map = {
            str(file1): "Financial_Documents",
            str(file2): "Personal_Photos"
        }

        result = organizer_service.organize_files(
            str(temp_folder),
            organization_map
        )

        assert result.ok
        assert result.data["organization"]["files_moved"] == 2
        assert (temp_folder / "Financial_Documents" / "financial_report.pdf").exists()
        assert (temp_folder / "Personal_Photos" / "vacation_photo.jpg").exists()

    def test_scan_folder(self, organizer_service, temp_folder):
        """Test folder scanning."""
        (temp_folder / "file1.txt").write_text("text")
        (temp_folder / "file2.pdf").write_text("pdf")
        (temp_folder / "subdir").mkdir()
        (temp_folder / "subdir" / "file3.txt").write_text("text")

        result = organizer_service.scan_folder(str(temp_folder))

        assert result.ok
        scan = result.data["scan"]
        assert scan["total_files"] == 3
        assert scan["total_folders"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
