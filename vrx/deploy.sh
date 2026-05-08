#! /bin/bash

image="ghcr.io/xtls/xray-core:latest"
keys_output=$(docker run --rm $image x25519)
uuid=$(docker run --rm $image uuid)
shortid=$(openssl rand -hex 4)
privkey=$(printf "%s\n" "$keys_output" | grep -oP 'PrivateKey: \K(.+)')
password=$(printf "%s\n" "$keys_output" | grep -oP 'Password: \K(.+)')
xhttp_path="/$(openssl rand -hex 2)"
default_port=8443
CLIENT_JSON="{\"id\": \"$uuid\", \"flow\": \"\"}"
URL="vless://$uuid@YOUR_SERVER_IP:$default_port?encryption=none&security=reality&sni=www.microsoft.com&fp=chrome&pbk=$password&sid=$shortid&type=xhttp&path=$xhttp_path#reality-xhttp"

cat > config.json << EOF
{
    "routing": {
        "domainStrategy": "AsIs",
        "rules": [
            {
                "type": "field",
                "domain": [
                    "geosite:google"
                ],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "domain": [
                    "geosite:cn"
                ],
                "outboundTag": "block"
            },
            {
                "type": "field",
                "ip": [
                    "geoip:cn"
                ],
                "outboundTag": "block"
            }
        ]
    },
    "inbounds": [
        {
            "listen": "0.0.0.0",
            "port": $default_port,
            "protocol": "vless",
            "settings": {
                "clients": [
                    $CLIENT_JSON
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "xhttp",
                "xhttpSettings": {
                    "path": "$xhttp_path"
                },
                "security": "reality",
                "realitySettings": {
                    "target": "www.microsoft.com:443",
                    "serverNames": [
                        "www.microsoft.com"
                    ],
                    "privateKey": "$privkey",
                    "shortIds": [
                       "$shortid"
                    ]
                }
            },
            "sniffing": {
                "enabled": true,
                "destOverride": [
                    "http",
                    "tls",
                    "quic"
                ]
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "tag": "direct"
        },
        {
            "protocol": "blackhole",
            "tag": "block"
        }
    ]
}
EOF


docker compose up -d


echo "Save the url for connection"
echo $URL
