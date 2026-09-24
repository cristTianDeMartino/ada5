"""Integration tests for the CLI interface.

Test Scenarios: TS-13 (CLI with results), TS-14 (CLI with error).
"""

import json
import subprocess
import sys
import os

import pytest

from src.cli import main as cli_main


@pytest.fixture(scope="module")
def sample_data_file(tmp_path_factory):
    """Create a temporary JSON file with sample customer data."""
    data = [
        {"id": "c001", "name": "María García", "email": "maria.garcia@example.com"},
        {"id": "c002", "name": "José López", "email": "jose.lopez@example.com"},
    ]
    filepath = tmp_path_factory.mktemp("data") / "customers.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(filepath)


def run_cli(query: str, data_file: str) -> subprocess.CompletedProcess:
    """Run the CLI as a subprocess."""
    env = os.environ.copy()
    env["CUSTOMER_DATA_FILE"] = data_file
    env["PYTHONUTF8"] = "1"  # Force UTF-8 mode on Windows
    return subprocess.run(
        [sys.executable, "-m", "src.cli", query],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )


class TestCLIWithResults:
    """TS-13: CLI search with results."""

    def test_search_mar_shows_results(self, sample_data_file):
        result = run_cli("mar", sample_data_file)
        assert result.returncode == 0
        assert "Found" in result.stdout
        assert "María García" in result.stdout

    def test_search_jose_accent_insensitive(self, sample_data_file):
        result = run_cli("jose", sample_data_file)
        assert result.returncode == 0
        assert "José López" in result.stdout

    def test_no_results_exit_0(self, sample_data_file):
        result = run_cli("zzzznotexist", sample_data_file)
        assert result.returncode == 0
        assert "No customers found" in result.stdout


class TestCLIWithErrors:
    """TS-14: CLI with validation errors."""

    def test_empty_query_exits_1(self, sample_data_file):
        result = run_cli("", sample_data_file)
        # Empty string in argv means the CLI receives "" which fails validation
        # But shell may pass it as empty arg, so we accept either exit 1 behaviors
        assert result.returncode == 1

    def test_empty_query_shows_error_on_stderr(self, sample_data_file):
        result = run_cli("", sample_data_file)
        assert result.returncode == 1
        # Either "Usage:" (no arg) or "Error:" (empty string validation)
        assert "Error" in result.stderr or "Usage" in result.stderr


class TestCLIMainDirect:
    """Direct unit tests for cli.main() to ensure code coverage."""

    def test_search_with_results(self, sample_data_file, capsys):
        exit_code = cli_main(args=["mar"], data_file=sample_data_file)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Found" in captured.out

    def test_search_no_results(self, sample_data_file, capsys):
        exit_code = cli_main(args=["zzzznotexist"], data_file=sample_data_file)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "No customers found" in captured.out

    def test_no_args_shows_usage(self, capsys):
        exit_code = cli_main(args=[], data_file="dummy.json")
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Usage" in captured.err

    def test_empty_query_validation_error(self, sample_data_file, capsys):
        exit_code = cli_main(args=[""], data_file=sample_data_file)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_double_space_validation_error(self, sample_data_file, capsys):
        exit_code = cli_main(args=["Ana  García"], data_file=sample_data_file)
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "consecutive spaces" in captured.err.lower()

    def test_missing_data_file(self, capsys):
        exit_code = cli_main(args=["test"], data_file="/nonexistent/file.json")
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

