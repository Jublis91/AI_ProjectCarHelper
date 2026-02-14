#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

QUESTIONS=(
  "What engine is in this car"
  "How do I troubleshoot starting issues"
  "What torque specs apply here"
  "Which parts are commonly replaced"
)

RAG_QUESTIONS=(
  "What engine is in this car according to the manual"
  "What torque specs are defined in the service documentation"
)

echo "Smoke test alkaa"
echo "BACKEND_URL=$BACKEND_URL"
echo ""

echo "Tarkistetaan backend /health"
health_json="$(curl -sS "$BACKEND_URL/health")"
echo "$health_json"

echo "$health_json" | python - <<'PY'
import sys, json
d = json.load(sys.stdin)
assert d.get("ok") is True, d
print("Backend OK")
PY
echo ""

echo "Varmistetaan että /ask toimii ilman LLM:ää (USE_OLLAMA=false oletus)"
ask_json="$(curl -sS -X POST "$BACKEND_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"smoke test without LLM","top_k":5}' \
  --max-time 20)"
echo "$ask_json"

echo "$ask_json" | python - <<'PY'
import sys, json
d = json.load(sys.stdin)

answer = d.get("answer")
sources = d.get("sources")
llm_mode = (d.get("llm_mode") or "").strip().lower()

assert isinstance(answer, str), f"answer not str: {type(answer)}"
assert isinstance(sources, list), f"sources not list: {type(sources)}"

# Tässä smoke testissä vaaditaan että LLM ei ole käytössä.
# Sallitaan "off" ja "rules" (jos sääntö osuu vahingossa).
assert llm_mode in ("off", "rules"), f"unexpected llm_mode: {llm_mode}"
print("OK: /ask ilman LLM:ää toimii")
PY
echo ""

echo "Mitataan /ask latenssi"
TIME_TOTAL=$(curl -s -o /dev/null \
  -w "%{time_total}" \
  -X POST "$BACKEND_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"latency test","top_k":5}' \
  --max-time 20)
echo "time_total: ${TIME_TOTAL} s"
echo ""

echo "Ajetaan 4 kysymystä"
for q in "${QUESTIONS[@]}"; do
  echo "Kysymys: $q"

  RESPONSE="$(curl -sS \
    -X POST "$BACKEND_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"$q\",\"top_k\":5}" \
    --max-time 20)"

  # Validointi: JSON muoto
  echo "$RESPONSE" | python - <<'PY'
import sys, json
json.load(sys.stdin)
PY

  ANSWER_TEXT="$(echo "$RESPONSE" | python - <<'PY'
import sys, json
d=json.load(sys.stdin)
print(d.get("answer",""))
PY
)"
  ANSWER_LEN=$(echo -n "$ANSWER_TEXT" | wc -c | tr -d ' ')

  SOURCES_COUNT="$(echo "$RESPONSE" | python - <<'PY'
import sys, json
d=json.load(sys.stdin)
s=d.get("sources") or []
print(len(s) if isinstance(s, list) else 0)
PY
)"
  LLM_MODE="$(echo "$RESPONSE" | python - <<'PY'
import sys, json
d=json.load(sys.stdin)
print((d.get("llm_mode") or "").strip())
PY
)"

  echo "answer_length: $ANSWER_LEN"
  echo "sources_count: $SOURCES_COUNT"
  echo "llm_mode: $LLM_MODE"
  echo ""
done

echo "Ajetaan 2 RAG-kysymystä ja vaaditaan sources_count > 0 (ilman LLM:ää)"
for q in "${RAG_QUESTIONS[@]}"; do
  echo "RAG kysymys: $q"

  RESPONSE="$(curl -sS \
    -X POST "$BACKEND_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"$q\",\"top_k\":5}" \
    --max-time 20)"

  SOURCES_COUNT="$(echo "$RESPONSE" | python - <<'PY'
import sys, json
d=json.load(sys.stdin)
s=d.get("sources") or []
print(len(s) if isinstance(s, list) else 0)
PY
)"

  LLM_MODE="$(echo "$RESPONSE" | python - <<'PY'
import sys, json
d=json.load(sys.stdin)
print((d.get("llm_mode") or "").strip().lower())
PY
)"

  echo "sources_count: $SOURCES_COUNT"
  echo "llm_mode: $LLM_MODE"

  # Varmista ettei LLM ole käytössä tässä smoke testissä
  if [ "$LLM_MODE" != "off" ] && [ "$LLM_MODE" != "rules" ]; then
    echo "FAIL. /ask käytti LLM:ää vaikka smoke test vaatii off. llm_mode=$LLM_MODE"
    exit 1
  fi

  if [ "$SOURCES_COUNT" -le 0 ]; then
    echo "FAIL. RAG-kysymys palautti 0 lähdettä."
    exit 1
  fi

  echo ""
done

echo "Smoke test ok"
