#! /bin/bash

CERT_DIR="conf/certs"
KEY="cert-key.pem"
CRT_REQ="crt.csr"
CERT="cert.pem"
EXT="ext.conf"

mkdir -p $CERT_DIR
pushd $CERT_DIR &> /dev/null

cat <<'EOF' > $EXT
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer:always
basicConstraints       = CA:FALSE
keyUsage               = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment, keyAgreement, keyCertSign
subjectAltName         = DNS:SERVER
issuerAltName          = issuer:copy
EOF

openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:secp384r1 -out $KEY
openssl req -batch -new -key $KEY -out $CRT_REQ -subj "/CN=SERVER"
openssl x509 -req -in $CRT_REQ -signkey $KEY -out $CERT -days 365 -sha256 -extfile $EXT &> /dev/null
rm -f $CRT_REQ $EXT

popd &> /dev/null