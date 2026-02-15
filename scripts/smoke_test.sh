#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
SMOKE_MODE="${SMOKE_MODE:-off}"  # off | ollama

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

py_json_ok() {
  python -c "import json,sys; json.loads(sys.argv[1]);" "$1" >/dev/null
}

py_get_health_ok() {
  python -c "import json,sys; d=json.loads(sys.argv[1]); assert d.get('ok') is True, d" "$1" >/dev/null
}

py_get_sources_count() {
  python -c "import json,sys; d=json.loads(sys.argv[1]); s=d.get('sources') or []; print(len(s) if isinstance(s,list) else 0)" "$1"
}

py_get_answer_len() {
  python -c "import json,sys; d=json.loads(sys.argv[1]); a=(d.get('answer') or ''); print(len(a.strip()))" "$1"
}

py_get_llm_mode() {
  python -c "import json,sys; d=json.loads(sys.argv[1]); print((d.get('llm_mode') or '').strip().lower())" "$1"
}

assert_llm_mode() {
  local mode="$1"
  if [ "$SMOKE_MODE" = "off" ]; then
    if [ "$mode" != "off" ] && [ "$mode" != "rules" ]; then
      echo "FAIL. SMOKE_MODE=off vaatii llm_mode=off|rules. llm_mode=$mode"
      exit 1
    fi
  elif [ "$SMOKE_MODE" = "ollama" ]; then
    if [ "$mode" != "ollama" ]; then
      echo "FAIL. SMOKE_MODE=ollama vaatii llm_mode=ollama. llm_mode=$mode"
      exit 1
    fi
  else
    echo "FAIL. Tuntematon SMOKE_MODE=$SMOKE_MODE (sallitut: off, ollama)"
    exit 1
  fi
}

echo "Smoke test alkaa"
echo "BACKEND_URL=$BACKEND_URL"
echo "SMOKE_MODE=$SMOKE_MODE"
echo ""

echo "Tarkistetaan backend /health"
health_json="$(curl -sS "$BACKEND_URL/health")"
echo "$health_json"
py_get_health_ok "$health_json"
echo "Backend OK"
echo ""

echo "Mitataan /ask latenssi"
TIME_TOTAL=$(curl -s -o /dev/null \
  -w "%{time_total}" \
  -X POST "$BACKEND_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"latency test","top_k":5}' \
  --max-time 180)
echo "time_total: ${TIME_TOTAL} s"
echo ""

echo "Ajetaan 4 kysymystä"
for q in "${QUESTIONS[@]}"; do
  echo "Kysymys: $q"

  RESPONSE="$(curl -sS \
    -X POST "$BACKEND_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"$q\",\"top_k\":5}" \
    --max-time 180)"

  py_json_ok "$RESPONSE"

  ANSWER_LEN="$(py_get_answer_len "$RESPONSE")"
  SOURCES_COUNT="$(py_get_sources_count "$RESPONSE")"
  LLM_MODE="$(py_get_llm_mode "$RESPONSE")"

  echo "answer_length: $ANSWER_LEN"
  echo "sources_count: $SOURCES_COUNT"
  echo "llm_mode: $LLM_MODE"

  assert_llm_mode "$LLM_MODE"

  if [ "$ANSWER_LEN" -le 0 ]; then
    echo "FAIL. answer_length <= 0"
    exit 1
  fi

  # Jos MIN_SCORE blokkaa, sources voi silti olla lista. Tässä vaaditaan >0 kuten sun aiempi testi.
  if [ "$SOURCES_COUNT" -le 0 ]; then
    echo "FAIL. sources_count <= 0"
    exit 1
  fi

  echo ""
done

echo "Ajetaan 2 RAG-kysymystä ja vaaditaan sources_count > 0"
for q in "${RAG_QUESTIONS[@]}"; do
  echo "RAG kysymys: $q"

  RESPONSE="$(curl -sS \
    -X POST "$BACKEND_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"$q\",\"top_k\":5}" \
    --max-time 180)"

  py_json_ok "$RESPONSE"

  ANSWER_LEN="$(py_get_answer_len "$RESPONSE")"
  SOURCES_COUNT="$(py_get_sources_count "$RESPONSE")"
  LLM_MODE="$(py_get_llm_mode "$RESPONSE")"

  echo "answer_length: $ANSWER_LEN"
  echo "sources_count: $SOURCES_COUNT"
  echo "llm_mode: $LLM_MODE"

  assert_llm_mode "$LLM_MODE"

  if [ "$ANSWER_LEN" -le 0 ]; then
    echo "FAIL. answer_length <= 0"
    exit 1
  fi

  if [ "$SOURCES_COUNT" -le 0 ]; then
    echo "FAIL. RAG-kysymys palautti 0 lähdettä."
    exit 1
  fi

  echo ""
done

echo "Smoke test ok"
