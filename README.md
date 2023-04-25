# tp1-redes-2023-1c

Para correr el programa primero se debe levantar un servidor con el comando 

python3 app_server.py -H "IP del server" -p "Puerto del server" -s "Directorio" 

Luego correr un cliente, para subir un archivo al servidor

python3 app_upload.py -H "IP del server" -p "Puerto del server" -s "Directorio del servidor" -n "Nombre del archivo"

para descargar un archivo del servidor

python3 app_download.py H "IP del server" -p "Puerto del server" -d "Directorio del servidor" -n "Nombre del archivo"

Deben exisitir los directorios y los archivos para que funcione correctamente

Para correr el mininet se utiliza el siguiente commando

sudo mn --custom ./mininet/custom.py --topo customTopo --mac -x
