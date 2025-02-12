@echo off
::This is a command file to genrate a self sign certificate using a root CA that use to sign server CA
if not exist rootCA.crt (
	echo [Generatring rootCA private key and Certificate..]
	openssl req -x509 -sha256 -days 3560 -nodes -newkey rsa:2048 -subj "/CN=Dvir Root Crt/C=IL/L=Zoran" -keyout rootCA.key -out rootCA.crt
)
echo [RootCA certificate exists skeipping file generation...]

if not exist server.key (
	echo [Generating server private key file : server.key ...]
	openssl genrsa -out server.key 2048
)
echo [Server private key file exists skippeing file generation..]
 
echo [Generating CSR file with server Private Key...]
openssl req -new -key server.key -out server.csr -config csr.conf

echo [Signing server certificate with rootCA and generating self signed Server.crt file...]
openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out server.crt -days 3650 -sha256 -extfile cert.conf
