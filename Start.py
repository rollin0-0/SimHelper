from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

def _ensure_python3_alias(runtime_root: Path) -> None:
    alias = runtime_root / "python" / "bin" / "python3"
    target = runtime_root / "python" / "bin" / "python3.10"
    if alias.exists() or (not target.exists()):
        return
    try:
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.symlink_to("python3.10")
    except OSError:
        return

def _runtime_candidates(base_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    for scope in (base_dir, base_dir.parent, base_dir.parent.parent):
        for root in (scope / "Tool" / "runtime", scope / "runtime"):
            _ensure_python3_alias(root)
            candidates.extend([
                root / "python" / "bin" / "python3",
                root / "python" / "bin" / "python3.10",
                root / "python" / "bin" / "python",
                root / "bin" / "python3",
                root / "bin" / "python",
                root / "python3",
                root / "python",
                root / "Python",
            ])
    deduped: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped

def _pick_runtime_python() -> Path | None:
    base_dir = Path(__file__).resolve().parent
    for candidate in _runtime_candidates(base_dir):
        try:
            if candidate.exists() and candidate.is_file() and os.access(candidate, os.X_OK):
                probe = subprocess.run([str(candidate), "-V"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                if probe.returncode == 0:
                    return candidate.resolve()
        except OSError:
            continue
    return None

def _maybe_reexec_with_runtime() -> None:
    if os.environ.get("SIM_SKIP_RUNTIME_REEXEC") == "1":
        return
    runtime_python = _pick_runtime_python()
    if not runtime_python:
        return
    current_python = Path(sys.executable).resolve()
    if current_python == runtime_python:
        return
    os.environ["SIM_SKIP_RUNTIME_REEXEC"] = "1"
    os.execv(str(runtime_python), [str(runtime_python), str(Path(__file__).resolve()), *sys.argv[1:]])

def _bootstrap_tool_path() -> None:
    base_dir = Path(__file__).resolve().parent
    tool_dir = base_dir / "Tool"
    if tool_dir.exists() and tool_dir.is_dir():
        tool_path = str(tool_dir.resolve())
        if tool_path not in sys.path:
            sys.path.insert(0, tool_path)

_maybe_reexec_with_runtime()
_bootstrap_tool_path()

from similarity_helper.p01a07fbe65ac0cb9af641964d8d46eac import main

if __name__ == "__main__":
    raise SystemExit(main())
