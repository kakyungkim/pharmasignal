#!/usr/bin/env bash
# 컷 한 장 생성. 기준 컷을 참조로 넣어 인물을 유지한다.
#   bash webtoon/gen_panel.sh 02 "장면 설명" "대사"
#
# 프롬프트는 stdin으로 넘긴다. 인자로 주면 따옴표와 줄바꿈이 섞여 깨진다.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="$1"; SCENE="$2"; LINE="$3"
REF="$ROOT/webtoon/_codex_test/panel_test.png"
OUT="$ROOT/webtoon/panels"
mkdir -p "$OUT"

PROMPT=$(cat <<PEOF
Generate one vertical Korean webtoon panel, 4:5 aspect ratio, and save it to
this exact path: $OUT/panel_$N.png

STYLE — match the attached reference image exactly: cel-shaded Korean webtoon
illustration, clean line art, soft gradient shading, muted navy and blue palette
with warm skin tones, cinematic lighting.

CHARACTER — the same woman as the attached reference, unchanged: late-20s Korean
woman, black shoulder-length hair, thin round silver-rimmed glasses, navy blazer
over a white shirt. Keep her face, hair and glasses identical to the reference.
Only the scene, pose and lighting change.

SCENE: $SCENE

SPEECH BUBBLE: a clean white rounded speech bubble containing exactly this Korean
text, spelled precisely, in a bold rounded Korean sans-serif: $LINE
Place the bubble where it does not cover her face.

Do not add any other text, captions, watermarks or signatures.
PEOF
)

echo "  [$N] 생성 중..."
printf '%s' "$PROMPT" | codex exec --skip-git-repo-check -s workspace-write \
  -C "$ROOT" -i "$REF" - > "/tmp/codex_panel_$N.log" 2>&1
if [ -f "$OUT/panel_$N.png" ]; then
  echo "  [$N] 완료 · $(du -h "$OUT/panel_$N.png" | cut -f1)"
else
  echo "  [$N] 실패"; tail -6 "/tmp/codex_panel_$N.log"
fi
