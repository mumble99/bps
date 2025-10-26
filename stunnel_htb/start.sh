#! /bin/bash

SERVER_IP="$1"
CONN_STRING="edge-us-starting-point-2-dhcp.hackthebox.eu:443"
IMAGE_NAME="stunnel-htb"
CONT_NAME="st-htb"
CONF_NAME="stunnel.conf"
CERT_DIR="certs"
CA_CERT="$CERT_DIR/ca-cert.pem"
CA_KEY="$CERT_DIR/ca-key.pem"
SERVER_CERT="$CERT_DIR/server-cert.pem"
SERVER_KEY="$CERT_DIR/server-key.pem"


generate_ca() {
    echo "Generate CA cert"

    dd if=/dev/urandom of=$CERT_DIR/rnd bs=256 count=1 2> /dev/null
    openssl req -new -x509 -days 10000 -batch -rand $CERT_DIR/rnd -config openssl.cnf -out $CA_CERT -keyout $CA_KEY 2> /dev/null
}


generate_signed_certs() {
    cert_path=$1
    key_path=$2

    echo "Generate cert"

    openssl genrsa -out $key_path 2048 2> /dev/null
    openssl req -new -key $key_path -out $CERT_DIR/req.csr -batch -config openssl.cnf 2> /dev/null
    openssl x509 -req -in $CERT_DIR/req.csr -CA $CA_CERT -CAkey $CA_KEY -CAcreateserial -out $cert_path -days 10000 2> /dev/null
}


example_conf() {
    cat << EOF > /dev/stdout
;#------CLIENT-------
[htb]
client = yes
accept = 127.0.0.1:65001
connect = $SERVER_IP:5051
CAfile = $CA_CERT
verifyChain = yes
;#####################

EOF
}


create_server_conf() {
    cat << EOF > $CONF_NAME
foreground = yes

[htb]
accept = 5051
connect = $CONN_STRING
CAfile = /etc/stunnel/ca.pem
cert = /etc/stunnel/cert.pem
key = /etc/stunnel/key.pem
verify = 0
EOF
}


stop() {
    docker stop $CONT_NAME &> /dev/null
    docker rm $CONT_NAME &> /dev/null
    docker rmi $IMAGE_NAME &> /dev/null
}



start() {
    echo "Example configuration for client"
    example_conf

    if [ ! -d $CERT_DIR ] ; then
        mkdir -p $CERT_DIR

        generate_ca

        generate_signed_certs $SERVER_CERT $SERVER_KEY

        echo "Create server config"
        create_server_conf

    fi

    echo "Build docker image"
    docker build -t $IMAGE_NAME . &> /dev/null

    echo "Start docker container"
    docker run -d -it --name $CONT_NAME -p 5051:5051 -v ./$CA_CERT:/etc/stunnel/ca.pem -v ./$SERVER_CERT:/etc/stunnel/cert.pem -v ./$SERVER_KEY:/etc/stunnel/key.pem -v ./$CONF_NAME:/etc/stunnel/stunnel.conf $IMAGE_NAME:latest
}


start
#stop
