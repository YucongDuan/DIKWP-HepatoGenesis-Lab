"""Strict data validation and deterministic serialization; no executable input."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any

class Invalid(ValueError):
    """A supplied research contract or artifact is invalid."""

def number(x: Any, name: str, minimum: float | None = None,
           maximum: float | None = None) -> float:
    try:
        valid = not isinstance(x, bool) and isinstance(x, (int, float)) and math.isfinite(x)
    except OverflowError:
        valid = False
    if not valid:
        raise Invalid(f"{name} must be a finite number, not a boolean.")
    if minimum is not None and x < minimum:
        raise Invalid(f"{name} must be at least {minimum}.")
    if maximum is not None and x > maximum:
        raise Invalid(f"{name} must be at most {maximum}.")
    return float(x)

def integer(x: Any, name: str, minimum: int = 0, maximum: int = 100000) -> int:
    if type(x) is not int or not minimum <= x <= maximum:
        raise Invalid(f"{name} must be an integer in [{minimum}, {maximum}].")
    return x

def identifier(value: Any, name: str = "id") -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value):
        raise Invalid(f"{name} must be 1-80 ASCII letters, digits, dots, dashes or underscores.")
    return value

def text(value: Any, name: str, limit: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise Invalid(f"{name} must be nonempty text of at most {limit} characters.")
    return value

def keys(obj: Any, allowed: set[str], required: set[str] = frozenset()) -> dict:
    if not isinstance(obj, dict):
        raise Invalid("Expected a JSON object.")
    if set(obj) - allowed or required - set(obj):
        raise Invalid(f"Unexpected keys: {sorted(set(obj)-allowed)}; missing keys: {sorted(required-set(obj))}.")
    return obj

def canonical(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise Invalid(f"Cannot serialize canonical JSON: {exc}") from exc

def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()

def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()

def loads(raw: str | bytes, max_bytes: int = 2_000_000) -> Any:
    if len(raw.encode("utf-8") if isinstance(raw, str) else raw) > max_bytes:
        raise Invalid("JSON input is too large.")
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise Invalid(f"Duplicate JSON key: {k}")
            result[k] = v
        return result
    def finite_float(raw_number):
        value = float(raw_number)
        if not math.isfinite(value):
            raise Invalid("Floating-point overflow in JSON number.")
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_float=finite_float,
                          parse_constant=lambda value: (_ for _ in ()).throw(Invalid(f"Invalid numeric constant: {value}")))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Invalid(f"Malformed JSON: {exc}") from exc

def load(path: Path) -> Any:
    p = Path(path)
    if p.stat().st_size > 2_000_000:
        raise Invalid("JSON input is too large.")
    return loads(p.read_bytes())

def atomic_text(path: Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".hepato-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def write_json(path: Path, obj: Any) -> None:
    canonical(obj)  # Validate before touching the destination.
    atomic_text(path, json.dumps(obj, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + "\n")

def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    import io
    if not fields or len(set(fields)) != len(fields) or any(set(r) != set(fields) for r in rows):
        raise Invalid("CSV rows must match a nonempty, unique, explicit schema.")
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        # Prevent formulas when a CSV is opened in spreadsheet software.
        writer.writerow({k: ("'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v)
                         for k, v in row.items()})
    atomic_text(path, out.getvalue())
