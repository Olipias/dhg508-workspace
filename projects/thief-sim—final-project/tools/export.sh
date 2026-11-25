#!/usr/bin/env bash
# 三平台桌面试玩包；默认新目录，保留旧包。可选 --with-web 保持旧接口。
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT_BIN:-$HOME/.local/bin/godot}"
VERSION="${RELEASE_VERSION:-0.26.16}"
OUTPUT="build/release-v${VERSION}-$(date +%Y%m%d-%H%M%S)"
WITH_WEB=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --output) [ "$#" -ge 2 ] || exit 2; OUTPUT="$2"; shift 2 ;;
        --with-web) WITH_WEB=1; shift ;;
        *) echo "用法: tools/export.sh [--output 目录] [--with-web]"; exit 2 ;;
    esac
done
mkdir -p "$OUTPUT/windows" "$OUTPUT/linux" "$OUTPUT/macos" "$OUTPUT/logs"
run_export() {
    local label="$1"; shift
    python3 tools/run_godot_check.py -- "$GODOT" "$@" > "$OUTPUT/logs/$label.log" 2>&1 || {
        tail -25 "$OUTPUT/logs/$label.log"; return 1;
    }
    if grep -E '^(ERROR|SCRIPT ERROR)|Failed to (load|open)' "$OUTPUT/logs/$label.log"; then
        return 1
    fi
    echo "$label 完成"
}
run_export import --headless --import
run_export windows --headless --export-release Windows "$OUTPUT/windows/thief-sim.exe"
run_export linux --headless --export-release Linux "$OUTPUT/linux/thief-sim.x86_64"
run_export macos --headless --export-release macOS "$OUTPUT/macos/thief-sim-macos.zip"
if [ "$WITH_WEB" -eq 1 ]; then
    mkdir -p "$OUTPUT/web"
    run_export web --headless --export-release Web "$OUTPUT/web/index.html"
fi
python3 tools/package_desktop.py "$OUTPUT" "$VERSION"
echo "发布包：$OUTPUT"
