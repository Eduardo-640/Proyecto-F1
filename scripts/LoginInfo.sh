#!/bin/bash
BASE_URL="http://localhost:8000/api"
echo "=== 1. Registro ==="
REGISTER_RESP=$(curl -s -X POST $BASE_URL/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"steam_id": "test_driver", "password": "test123", "name": "Test", "last_name": "Driver"}')
echo "$REGISTER_RESP" | jq .
# Extraer token del registro
ACCESS=$(echo "$REGISTER_RESP" | jq -r '.access')
REFRESH=$(echo "$REGISTER_RESP" | jq -r '.refresh')
echo ""
echo "=== 2. Perfil (con token del registro) ==="
curl -s $BASE_URL/auth/profile/ -H "Authorization: Bearer $ACCESS" | jq .
echo ""
echo "=== 3. Login ==="
LOGIN_RESP=$(curl -s -X POST $BASE_URL/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"steam_id": "test_driver", "password": "test123"}')
echo "$LOGIN_RESP" | jq .
echo ""
echo "=== 4. Refresh Token ==="
curl -s -X POST $BASE_URL/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq .
echo ""
echo "=== 5. Drivers públicos ==="
curl -s $BASE_URL/public/drivers/ | jq .
