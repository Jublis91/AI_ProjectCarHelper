#!/usr/bin/env bash
set -e

BACKEND_URL="http://localhost:8000"

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

echo "Tarkistetaan backend /health"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
if [ "$STATUS" -ne 200 ]; then
  echo "Backend ei ole käynnissä. HTTP $STATUS"
  exit 1
fi
echo "Backend OK"
echo ""

echo "Mitataan /ask latenssi"
TIME_TOTAL=$(curl -s -o /dev/null \
  -w "%{time_total}" \
  -X POST "$BACKEND_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"latency test"}' \
  --max-time 10)
echo "time_total: ${TIME_TOTAL} s"
echo ""

echo "Ajetaan 4 kysymystä"
for q in "${QUESTIONS[@]}"; do
  echo "Kysymys: $q"

  RESPONSE=$(curl -s \
    -X POST "$BACKEND_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"$q\"}" \
    --max-time 10)

  ANSWER_TEXT=$(echo "$RESPONSE" | sed -n 's/.*"answer":"\([^"]*\)".*/\1/p')
  ANSWER_LEN=$(echo -n "$ANSWER_TEXT" | wc -c)

  SOURCES_COUNT=$(echo "$RESPONSE" | grep -o '"source"' | wc -l | tr -d ' ')

  echo "answer_length: $ANSWER_LEN"
  echo "sources_count: $SOURCES_COUNT"
  echo ""
done

echo "Ajetaan 2 RAG-kysymystä ja vaaditaan sources_count > 0"
for q in "${RAG_QUESTIONS[@]}"; do
  echo "RAG kysymys: $q"

  RESPONSE=$(curl -s \
    -X POST "$BACKEND_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"$q\"}" \
    --max-time 10)

  SOURCES_COUNT=$(echo "$RESPONSE" | grep -o '"source"' | wc -l | tr -d ' ')
  echo "sources_count: $SOURCES_COUNT"

  if [ "$SOURCES_COUNT" -le 0 ]; then
    echo "FAIL. RAG-kysymys palautti 0 lähdettä."
    exit 1
  fi

  echo ""
done

echo "Smoke test ok"
