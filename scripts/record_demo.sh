#!/usr/bin/env bash
# 데모 영상 녹화. 제출물 심사가 1차 관문인 대회에서는 슬라이드보다 영상이 낫다.
#
#   bash scripts/record_demo.sh "antibody-drug conjugate"
#
# macOS 기본 도구만 쓴다. 터미널 창을 녹화하므로 실행 전에 글자를 키우고
# 창을 화면 가운데로 옮겨 둘 것. 종료는 Ctrl+C.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOPIC="${1:-antibody-drug conjugate}"
OUT="$ROOT/video"
mkdir -p "$OUT"
FILE="$OUT/demo.mov"

command -v screencapture >/dev/null || { echo "screencapture 없음 (macOS 전용)"; exit 1; }

printf '\n녹화 대상: %s\n' "$TOPIC"
printf '저장 위치: %s\n' "$FILE"
printf '\n3초 뒤 시작합니다. 터미널 창을 앞으로 가져오세요.\n'
sleep 3

# 화면 녹화를 백그라운드로 띄우고 파이프라인을 실행
screencapture -v "$FILE" &
REC=$!
sleep 2

cd "$ROOT/code" || exit 1
PYTHONPATH=src "${PYTHON:-python3}" -m pharmasignal.cli run "$TOPIC" --limit 20

sleep 2
kill -INT "$REC" 2>/dev/null
wait "$REC" 2>/dev/null

printf '\n녹화 완료: %s\n' "$FILE"
printf '용량이 크면 아래로 줄인다(ffmpeg 필요).\n'
printf '  ffmpeg -i %s -vcodec libx264 -crf 28 %s/demo.mp4\n\n' "$FILE" "$OUT"
