# Repository Guidelines

## Project Structure & Module Organization
- `convnew/`: Source package (`main.py` provides the CLI and core conversion logic).
- `backup/`: Legacy/reference implementations; do not modify unless migrating fixes back.
- `build/`, `dist/`: Build artifacts (PyInstaller outputs). Never commit changes here.
- Test utilities live at repo root as scripts: `test_*.py` and sample assets like `test_input.jpg`.

## Build, Test, and Development Commands
- Install editable: `pip install -e .` (uses `pyproject.toml`).
- Run converter (E6): `python -m convnew.main image.jpg --preset photo --method floyd --dir auto --palette e6`.
- Run converter (E7): `python -m convnew.main image.jpg --palette e7`.
- Quick test image: `python test_color.py` (generates `test_colors.jpg`).
- Firmware compatibility check: conversion prints results automatically; to recheck an output BMP: `python -m convnew.main out_e6.bmp --test-only --palette e6` or `--palette e7`.
- Build Windows exe: `./build_exe.ps1` (or `pyinstaller --onefile --name ConvNew ./convnew/main.py`).

## Coding Style & Naming Conventions
- Python 3.7+; follow PEP 8, 4‑space indents, 100‑char line guide.
- Names: modules/files `lower_snake_case`, functions/vars `snake_case`, constants `UPPER_SNAKE_CASE`.
- Prefer type hints and docstrings on public functions; keep CLI help clear and concise.
- Avoid edits in `build/`, `dist/`; keep `backup/` read‑only unless specifically improving parity.

## Testing Guidelines
- No formal test framework required; use provided scripts:
  - `python test_firmware_compat.py` runs conversion modes and validates E6 color compliance.
  - `python test_optimized.py`, `python test_color_fix.py`, `python test_e6_colors.py` for targeted checks.
- Outputs should include `*_e6.bmp` and `*_preview.png`; BMP must contain only the six E6 colors.

## Commit & Pull Request Guidelines
- Commit messages: concise, imperative (e.g., "add dithering option"), reference issues when applicable.
- PRs should include: summary, rationale, sample command(s) used, and before/after previews when image quality changes.
- Update `README.md` and CLI `--help` when flags or behavior change.

## Agent‑Specific Instructions
- Keep patches minimal and scoped; do not modify `build/`, `dist/`, or large binaries.
- When altering conversion logic, validate with `test_firmware_compat.py` and a sample run of `python -m convnew.main test_input.jpg`.
- If adding files or flags, reflect changes in `README.md` and this guide.
