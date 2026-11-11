#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

python_bin="${PYTHON_BIN:-}"
if [[ -z "$python_bin" ]] && command -v python3 >/dev/null 2>&1; then
  python_bin="$(command -v python3)"
fi
if [[ -z "$python_bin" ]] && command -v python >/dev/null 2>&1; then
  python_bin="$(command -v python)"
fi
if [[ -z "$python_bin" ]]; then
  echo "Python 3.9 or newer is required." >&2
  exit 127
fi

exec "$python_bin" "$script_dir/Export-VibeLabAndroid.py" "$@"
