"""Test ShareSight support."""

import subprocess
import sys


def test_run_custom_div_0() -> None:
    """
    Test based on a failing scenario.

    This fails in the original version because of
    division by zero in bed and breakfasting.
    """
    cmd = [
        sys.executable,
        "-m",
        "cgt_calc.main",
        "--year",
        "2020",
        "--custom",
        "tests/test_data/custom/div0.csv",
        "--no-pdflatex",
        "--no-balance-check",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True)
    assert result.stderr == b"", "Run with example files generated errors"
