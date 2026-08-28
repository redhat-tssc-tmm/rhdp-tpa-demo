#!/bin/bash
set -euo pipefail

TPA_NAMESPACE="trusted-profile-analyzer"
KEYCLOAK_NAMESPACE="keycloak"
OIDC_SECRET_NAME="oidc-cli"
OIDC_CLIENT_ID="tpa-cli"
OIDC_REALM="tssc-sso"

# --- 1) Ask for the filename ---
if [[ $# -ge 1 ]]; then
  DATASET_FILE="$1"
else
  read -rp "Path to dataset file: " DATASET_FILE
fi

if [[ ! -f "$DATASET_FILE" ]]; then
  echo "Error: file not found: $DATASET_FILE"
  exit 1
fi

FILE_SIZE=$(du -h "$DATASET_FILE" | cut -f1)
echo "Using dataset: $DATASET_FILE ($FILE_SIZE)"

# --- 2) Gather cluster info ---
echo "Retrieving TPA route..."
TPA_HOST=$(oc get route tpa-short-url -n "$TPA_NAMESPACE" -o jsonpath='{.spec.host}' 2>/dev/null) || \
TPA_HOST=$(oc get routes -n "$TPA_NAMESPACE" -o jsonpath='{.items[0].spec.host}')
TPA_URL="https://${TPA_HOST}"
echo "TPA endpoint: $TPA_URL"

echo "Retrieving Keycloak route..."
KC_HOST=$(oc get route keycloak -n "$KEYCLOAK_NAMESPACE" -o jsonpath='{.spec.host}')
KC_TOKEN_URL="https://${KC_HOST}/realms/${OIDC_REALM}/protocol/openid-connect/token"
echo "Token endpoint: $KC_TOKEN_URL"

echo "Retrieving OIDC client secret..."
CLIENT_SECRET=$(oc get secret "$OIDC_SECRET_NAME" -n "$TPA_NAMESPACE" -o jsonpath='{.data.client-secret}' | base64 -d)

# --- 3) Get authentication token ---
echo "Requesting access token..."
RESPONSE=$(curl -sSk "$KC_TOKEN_URL" \
  -d "grant_type=client_credentials&client_id=${OIDC_CLIENT_ID}&client_secret=${CLIENT_SECRET}")

TOKEN=$(echo "$RESPONSE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])' 2>/dev/null) || {
  echo "Error: failed to obtain access token"
  echo "Response: ${RESPONSE:0:300}"
  exit 1
}
echo "Access token obtained."

# --- 4) Upload the dataset ---
echo "Uploading $DATASET_FILE to ${TPA_URL}/api/v3/dataset ..."
HTTP_CODE=$(curl -sk -o /tmp/tpa-upload-response.json -w "%{http_code}" -X POST \
  "${TPA_URL}/api/v3/dataset" \
  -H "Content-Type: application/zip" \
  -H "Authorization: Bearer ${TOKEN}" \
  --data-binary @"$DATASET_FILE") || true

echo "HTTP response: ${HTTP_CODE:-unknown}"

if [[ "$HTTP_CODE" =~ ^2 ]]; then
  echo "Upload successful."
elif [[ "$HTTP_CODE" == "504" || -z "$HTTP_CODE" || "$HTTP_CODE" == "000" ]]; then
  echo "Route timed out but upload likely completed — server continues processing."
else
  echo "Upload failed (HTTP $HTTP_CODE)."
  cat /tmp/tpa-upload-response.json 2>/dev/null || true
  exit 1
fi


echo ""
echo "Done."
