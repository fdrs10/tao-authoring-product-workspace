"""§55-adjacent guard: every web/ ES module must parse as ESM.

Plain ``node --check`` silently PASSES files containing ``import``/``export``
(verified 2026-10-15: a file with a paren error + an import statement exits 0),
which let two real syntax errors reach Chromium during Phase 4/5. This gate
feeds each file to Node as an explicit module via stdin and requires a zero
exit code. Skipped when Node is not installed.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

WEB_DIR = Path(__file__).resolve().parents[2] / "web"


def _js_files():
    return sorted(WEB_DIR.rglob("*.js"))


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("path", _js_files(), ids=lambda p: str(p.relative_to(WEB_DIR)))
def test_web_js_parses_as_esm(path):
    # stdin forces module parsing regardless of extension/package type; the
    # exit code is read directly (no pipeline masking).
    proc = subprocess.run(
        ["node", "--input-type=module", "--check"],
        stdin=open(path, "rb"),
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, f"{path} does not parse as ESM:\n{proc.stderr}"
