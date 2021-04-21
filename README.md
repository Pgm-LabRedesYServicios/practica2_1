Profes:
 - Antonio García Herraiz (p2)
 - José Manuel Giménez Guzmán (p1)

# Jueves 11 febrero 2021: 

Hemos empezado creando una máquina virtual usando Ubuntu 18.04.5 LTS,
nada más instalar la distribución, actualizamos los paquetes con
`sudo apt update && sudo apt upgrade`, configuramos el demonio de ssh
editando el archivo `/etc/ssh/sshd_config` para moverlo del puerto 22
al 3524 para evitar posibles ataques (quedando pendiente el
deshabilitar el inicio de sesión con contraseña). 

Luego, habilitamos el servicio de ssh con
`sudo systemctl enable –now sshd` y configuramos el router del equipo
donde está instalado para permitir el acceso desde internet a la
máquina virtual y además le asignamos una IP fija a la máquina virtual
en base a su MAC. 

# Domingo 14 febrero 2021: 
Creamos claves publicas y privadas para acceder al servidor y
configuramos este para solo aceptar las conexiones con esas claves. 

Nos bajamos el repositorio de git de asterisk y tras hacer un checkout
de la versión 18.2.0, procedimos a mirar las dependencias de este
programa para bajarlas. Tuvimos que descargar con el gestor de paquetes
apt e instalar las siguientes librerías para descargar Asterisk. 

Tras mirar las dependencias necesarias para instalar asterisk,
intentamos instalar las librerías listadas en el README, pero tras
fallar el `./configure` , nos remitimos al paquete oficial e instalamos
las dependencias de construcción listadas. La única que no pudimos
instalar por no ser encontrada fue libpjproject-dev, pero al ejecutar
`./configure` no salió ningún error. 

Tras ello, ejecutamos `make`, `sudo make install` y `sudo make samples`

# Jueves 18 febrero 2021:
Tras intentar instalar otros módulos desde el gestor de paquetes, nos
ha dado errores de colisión en el sistema de archivos. Debido a esto,
desinstalamos con `sudo make uninstall` y para solucionarlos ejecutamos

```
sudo dpkg --configure -a
sudo apt-get remove asterisk asterisk-voicemail
sudo apt-get clean
sudo apt-get update
sudo apt autoremove
```

Hemos vuelto a empezar la instalacion, pero esta vez de la siguiente
forma:

```
make clean

sudo contrib/scripts/get_mp3_source.sh
sudo contrib/scripts/install_prereq install

./configure

rm menuselect.makeopts
make menuselect
```

En menuselect hemos escogido el adaptador a mysql, hemos añadido las
voces en español, chan\_ooh323, app\_macro y format\_mp3. Después de
seleccionar las opciones, hemos compilado el software con `make`.

Tras finalizar, con `sudo make install` y `sudo make samples`
terminamos de instalar.

Tras hacer la instalacion, modificamos `/etc/asterisk/cel.conf` y
`/etc/asterisk/cdr.conf` apuntando radiuscfg a
`/etc/radcli/radiusclient.conf` y hemos hecho un enlace simbólico
de `/etc/radiusclient-ng` a `/etc/radcli`.

Al final de la configuración habilitamos el socket unix para poder
conectarnos al servicio con `asterisk -rvv`, esto lo hacemos
modificando `/etc/asterisk/asterisk.conf`, añadiendo al final del
archivo.

```conf
[files]
astctlpermissions = 0660
astctlowner = asterisk
astctlgroup = asterisk
astctl = asterisk.ctl
```

# Jueves 25 Febrero 2021:
Tras hacer una configuración inicial de PJSIP, generamos un certificado
auto firmado de SSL

```sh
# Generamos el certificado valido por 365 dias de 4096 bits
openssl req -newkey rsa:4096 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
# Combinamos el certificado con la clave en un PKCS#12
openssl pkcs12 -inkey key.pem -in certificate.pem -export -out certificate.p12

# Con estos comandos podemos ver el resultado de las operaciones anteriores
openssl x509 -text -noout -in certificate.pem
openssl pkcs12 -in certificate.p12 -noout -info
```

Desde los repositorios instalamos Postgres para integrarlo en asterisk
y habilitamos el servicio de la base de datos:
```sh
sudo systemctl enable --now postgresql.service
```

Una vez arrancado el servicio, ejecutamos el script para crear la base
de datos de asterisk con `sudo -u postgres psql -a -q -f asterisk.sql`

El script en cuestion es:
```sql
CREATE USER asterisk WITH ENCRYPTED PASSWORD 'Obelix' CREATEDB;
CREATE DATABASE asterisk OWNER=asterisk;
\c asterisk;
CREATE TABLE cdr (
    calldate timestamp NOT NULL ,
    clid varchar (80) NOT NULL ,
    src varchar (80) NOT NULL ,
    dst varchar (80) NOT NULL ,
    dcontext varchar (80) NOT NULL ,
    channel varchar (80) NOT NULL ,
    dstchannel varchar (80) NOT NULL ,
    lastapp varchar (80) NOT NULL ,
    lastdata varchar (80) NOT NULL ,
    duration int NOT NULL ,
    billsec int NOT NULL ,
    disposition varchar (45) NOT NULL ,
    amaflags int NOT NULL ,
    accountcode varchar (20) NOT NULL ,
    uniqueid varchar (150) NOT NULL ,
    userfield varchar (255) NOT NULL ,
    peeraccount varchar(20) NOT NULL,
    linkedid varchar(150) NOT NULL,
    sequence int NOT NULL
);
GRANT ALL ON ALL TABLES IN SCHEMA public TO asterisk;
```

# Jueves 4 marzo 2021: 
Empezamos a seguir la documentacion oficial publicada en el [link](https://wiki.asterisk.org/wiki/display/AST/Hello+World)

# Jueves 11 marzo 2021:
## Configuración de conexión con Postgres
Configuramos el conector con la base de datos Postgres en el archivo
`cdr_pgsql.conf`:

``` ini
[global]
hostname=localhost
port=5432
dbname=asterisk
user=asterisk
password=Obelix
;appname=asterisk    ; Postgres application_name support (optional). Whitespace not allowed.
table=cdr           ; SQL table where CDRs will be inserted
encoding=utf8       ; Encoding of logged characters in Asterisk
timezone=UTC        ; Uncomment if you want datetime fields in UTC/GMT
```

Para hacerlo efectivo, tenemos que cargar el módulo de Postgres en `modules.conf`

``` ini
preload => res_config_pgsql.so
```

Dentro de `res_odbc.conf` activamos el servicio de logging y le pasamos los
credenciales para conectarse con la base de datos:

``` ini
;
; Permit disabling sections without needing to comment them out.
; If not specified, it is assumed the section is enabled.
enabled => yes

; What should we execute to ensure that our connection is still alive?  The
; statement should return a non-zero value in the first field of its first
; record.  The default is "select 1".
sanitysql => select 1

; Enable query logging. This keeps track of the number of prepared queries
; and executed queries as well as the query that has taken the longest to
; execute. This can be useful for determining the latency with a database.
; The data can be viewed using the "odbc show" CLI command.
; Note that only successful queries are logged currently.
logging => yes

; Credentials to access the db
username => asterisk
password => Obelix
```

## Configuración de PJSIP
Una vez configurada la conexión con Postgres, configuramos PJSIP, que será el
medio por el cual los usuarios del servicio de telefonía se conectarán con
asterisk.

En el archivo `pjsip.conf` configuramos lo básico, limitamos el reenvio a 70
saltos, definimos un `user_agent`, especificamos que el dominio por defecto es
`localhost` y que mande un `keep_alive` cada 300 ms

``` ini
[global]
max_forwards=70
user_agent=LabRedes PBX
default_realm=localhost
keep_alive_interval=300
```

Luego escribimos lo siguiente 3 veces (cambiando 6001 por 6002 y 6003 en cada caso):

``` ini
; == Numeros de llamar
[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001
aors=6001

[6001]
type=auth
auth_type=userpass
password=unsecurepassword
username=6001

[6001]
type=aor
max_contacts=1
```

De esta forma definimos en el contexto `from-internal` los usuarios 6001, 6002 y
6003.

También, para poder llamar, habilitamos los transportes udp, tcp y wss:

``` ini
; == Transports

[udp_transport]
type=transport
protocol=udp
bind=0.0.0.0
tos=af42
cos=3

[wss_transport]
type=transport
protocol=wss
bind=0.0.0.0

[tcp_transport]
type=transport
protocol=tcp
bind=0.0.0.0
```

## Configuración general del dialplan

En el dialplan se configuran todos los puntos de entrada para llamadas, para
en el archivo `extensions.conf` escribimos el siguiente bloque para evitar
que los bloques de configuración se puedan mezclar y evitar reescribir la
configuración del dialplan

``` ini
[general]
static=yes
writeprotect=yes
priorityjumping=no
autofallthrough=no
```

Al final del bloque `from-internal` del dialplan, ponemos una extensión
que cuelgue directamente toda llamada a extensión no definida:

``` ini
exten => e,1,Hangup()
```

## Configuración llamada normal
Definimos el contexto del dialplan `from-internal` y ahí configuramos para cada
usuario la extensión con su número correspondiente. Primero se especifica que
mediante `Dial` se intente llamar usando PJSIP al número marcado y si no hay
respuesta tras 30 segundos, que se desvie al buzón de voz.

``` ini
[from-internal]
exten => _6001,1,NoOp(Llamando al 6001)
 same => n,Dial(PJSIP/6001,30)
 same => n,VoiceMail(6001@from-internal,u)
 same => n,Hangup()
```

## Configuración de buzón de voz
Para el buzón de voz, habiendo especificado previamente en el dialplan que si en
la llamada directa a un número no se coge, se ejecute la aplicación `VoiceMail`,
configuramos los buzones de los 3 usuarios en el archivo `voicemail.conf`.

En este archivo especificamos que la contraseña es 8888, el nombre y correos
ficticios. También que el número máximo de mensajes en el buzón es 10.

```ini
[from-internal]
6001 => 8888,Paquito Txokolatero,paquito@example.com,paquito2@example.com,attach=no|tz=central|maxmsg=10
6002 => 8888,Jose Ortega y Gasset,jose@example.com,jose2@example.com,attach=yes|tz=eastern|maxmsg=10
6002 => 8888,Manuela Carmena Vuelve,manuela@example.com,manuela2@example.com,attach=yes|tz=eastern|maxmsg=10
```

```ini
; Voice Mail entry
exten => _6500,1,Answer(500)
 same => n,VoiceMailMain(@from-internal)
```

## Configuración de sala de llamada
La aplicación del Dialplan `ConfBridge` nos permite crear salas de conferencia,
para hacer uso de ella, primero configuramos `confbridge.conf` para que tenga el
idioma en español:

``` ini
sound_only_person => /var/lib/asterisk/sounds/es/conf-onlyperson ; The sound played when the user is the only person in the conference.
sound_only_one => /var/lib/asterisk/sounds/es/confbridge-only-one ; The sound played to a user when there is only one other
```

En el dialplan habilitamos un punto de entrada para poder llamar a una sala:

``` ini
exten => _6000,1,NoOp(Llamando al 6000)
 same => n,Answer()
 same => n,ConfBridge(6000)
 same => n,Log(NOTICE, 6000 Call result ${DIALSTATUS})
 same => n,Hangup()
```

## Resumen

Con estos cambios, los servicios quedan de tal forma:

Extensión | Servicio
----------|---------
6001 | Llamar al 6001
6002 | Llamar al 6002
6003 | Llamar al 6003
6500 | Configurar el buzón de voz
6000 | Sala de conferencia / llamada grupal

# Lunes 15 marzo 2021:

Implementamos el desvío de llamadas editando el dialplan, 

``` ini
; --- Individual phone config
exten => _6001,1,NoOp(Llamando al ${EXTEN})
 same => n,Set(REDIRECTNUM=${DB(REDIRECT/${EXTEN})})
 same => n,GotoIf($[${ISNULL(${REDIRECTNUM})}]?internal:redirect)
 same => n(internal),Dial(PJSIP/${EXTEN},30)
 same => n,VoiceMail(${EXTEN}@from-internal,u)
 same => n(redirect),Dial(PJSIP/${REDIRECTNUM},30)
 same => n,Hangup()

; --- Call Forwarding
; Set number to forward
exten => *21,1,Playback(hello)
 same => n,Playback(vm-enter-num-to-call)
 same => n,Read(cfwd)
 same => n,Playback(beep)
 same => n,Set(DB(REDIRECT/${CALLERID(num)})=${cfwd})
 same => n,Set(DB(REDIRTIMER/TIMER)=10)
 same => n,Playback(you-entered)
 same => n,SayDigits(${DB(REDIRECT/${CALLERID(num))}})
 same => n,Playback(enabled)

; Disable forwarding
exten => *22,1,Set(NOREDIRNUM=${DB_DELETE(REDIRECT/${CALLERID(num)})})
 same => n,Playback(disabled)
```

Con estos cambios, los servicios nuevos quedan de tal forma:

Extensión | Servicio
----------|---------
\*21 | Activar y/o cambiar número de desvio de llamada
\*22 | Desactivar desvio de llamada

# Jueves 18 marzo 2021:
Para hacer el callcenter, debido a la relativa complejidad de la lógica a
expresar en el dialplan, lo escribimos en lua. Para ello, editamos el archivo
`extensions.lua`:

``` lua
extensions = {
    ["from-internal"] = {
        ["11888"] = function()
            counter = 0
            app.Answer()

            while(counter < 5)
            do
                app.Playback("vm-enter-num-to-call")
                app.Read("department")
                app.Playback("beep")

                dep = channel.department:get()
                app.Playback("you-entered")
                app.SayDigits(dep)

                num = tonumber(dep)

                if(num ~= nil and num <= 3 and num >= 0)
                then
                    break
                else
                    app.Playback("vm-sorry")
                    counter = counter + 1
                end
            end
            app.Dial("PJSIP/600" .. dep, 30)
            app.Hangup()
        end;
    }
}
```

Con este cambio, el servicio queda de tal forma:

Extensión | Servicio
----------|---------
11888 | Callcenter para llamar al 6001, 6002 o 6003

# Jueves 15 abril 2021:
En el archivo de agentes, como ha cambiado la configuracion, simplemente
adaptamos la que hay de ejemplo.

```ini
[general]
[template-agent](!)
autologoff=15
ackcall=yes
acceptdtmf=#
musiconhold=default

; Define agent 6001 using the my-agents template:
[6001](template-agent)
fullname=Mark Spencer
;
; Define agent 6002 using the my-agents template:
[6002](template-agent)
fullname=Tommy Jerry

; Define agent 6003 using the my-agents template:
[6003](template-agent)
fullname=Aitor Menta
```

Despues de tener los agentes definidos, configuramos una cola en `queues.conf`
```ini
[ColaUno]
music=default
strategy=ringall
timeout=15
retry=5
wrapuptime=0
maxlen=0
announce-frequency=0
announce-holdtime=no
member => Agent/6001,1
member => Agent/6002,1
member => Agent/6003,1
```

Para poder usar los agentes y la cola definimos dos puntos de entrada, uno para
logear a los agentes (sin autenticar) y el otro (8001) para llamar a la ColaUno
```ini
exten => _7XXX,1,Answer(500)
 same => n,Log(NOTICE, $[${EXTEN} - 1000])
 same => n,AgentLogin($[${EXTEN} - 1000])
 same => n,Hangup()

exten => 8001,1,Answer(500)
 same => n,Queue(ColaUno)
 same => n,Hangup()
```

# Domingo 18 Abril 2021:

Tras leer la escasa documentacion y los ejemplos, nos dimos cuenta que para
añadir agentes a la cola ha cambiado la sintaxis. Así que en el archivo
`queues.conf` cambiamos las últimas líneas por las siguientes:

```ini
member => Local/6001@from-internal,0,Mark Spencer,Agent:6001
member => Local/6002@from-internal,0,Tommy Jerry,Agent:6002
member => Local/6003@from-internal,0,Aitor Menta,Agent:6003
```

[Aquí](https://github.com/Pgm-LabRedesYServicios/practica2_1/commit/a9fe85990e7872d2f4d1b389cc05f6d65ba8dcab#diff-5e39347bfc125fb83ccc3d2405bb7fd45508f6dcf51c0c3a9b76c322204e297b)
se puede ver el diff del commit.

Dado que puede ser molesto estar escuchando las música de espera y tener la
línea únicamente habilitada para el callcenter, habilitamos el poder asignar
una línea a la cola de forma dinámica sin tener que ser agente, se accede a
esta funcionalidad marcando el 7001 y para dejar de recivir llamadas, el 7002.

Un inconveniente de esta modalidad para entrar en cola es que si no se llama al
7002 antes de cerrar la sesión del teléfono con la centralita, este número
seguirá registrado para seguir atendiendo llamadas cuando se vuelva a conectar.

```ini
exten => 7000,1,Log(NOTICE, $[${EXTEN} - 1000] calling from ${CALLERID(num)})
 same => n,Answer()
 same => n,AgentLogin(${CALLERID(num)})
 same => n,Playback(beep)
 same => n,Hangup()

exten => 7001,1,Log(NOTICE, $[${EXTEN} - 1000] calling from ${CALLERID(num)})
 same => n,Answer()
 same => n,AddQueueMember(ColaUno,PJSIP/${CALLERID(num)})
 same => n,Playback(beep)
 same => n,Hangup()

exten => 7002,1,Log(NOTICE, $[${EXTEN} - 1000] calling from ${CALLERID(num)})
 same => n,Answer()
 same => n,RemoveQueueMember(ColaUno,PJSIP/${CALLERID(num)})
 same => n,Playback(beep)
 same => n,Hangup()
```
    
## Resumen

Con estos cambios, los servicios quedan de tal forma:

Extensión | Servicio
----------|---------
7000 | Inicio de sesión como agente
7001 | Poner número para antender llamadas en la cola
7002 | Dejar de atender llamadas en la cola
8001 | Llamar para entrar en cola

# Lunes 19 Abril 2021:
## ARI
Habilitamos el servicio de la API y lo abrimos para poder acceder a este desde
otros dispositivos (esto es muy inseguro y debería de configurarse otro
servicio para únicamente permitir a ciertos usuarios ya que estos servicios
permiten leer y manipular la configuración de asterisk).

Para habilitar la ARI, cambiamos el archivo `ari.conf`:

``` ini
[general]
enabled = yes       ; When set to no, ARI support is disabled.
pretty = yes        ; When set to yes, responses from ARI are
                    ; formatted to be human readable.
allowed_origins = *  ; Comma separated list of allowed origins, for
                     ; Cross-Origin Resource Sharing. May be set to * to
                     ; allow all origins.
[asterisk]
type = user        ; Specifies user configuration
read_only = no     ; When set to yes, user is only authorized for
                   ; read-only requests.
password = asterisk      ; Crypted or plaintext password (see password_format).
password_format = plain  ; When set to plain, the password is in plaintext.
```

Aquí especificamos que la API Rest está habilitada, como no es un servidor de
producción, que las respuestas de la API están formateadas para que sean
legibles a los humanos y permitimos el acceso a todos los orígenes.

En el apartado de `[asterisk]` definimos al usuario de la API asterisk, con
contraseña asterisk y le damos permiso de escritura.

También se necesita abrir el servidor de asterisk para que responda a queries
fuera de localhost, para ello editamos el archivo `http.conf`:

``` ini
bindaddr=0.0.0.0
```

## AMI
Para poder hacer uso de esta API, tenemos que habilitarla en el archivo
`manager.conf`:

``` ini
[general]
enabled = yes

[username]
secret=password
permit=0.0.0.0/0.0.0.0
read = all
write = all
```

## Docker
Para empezar a empaquetar en un contenedor la aplicación, creamos un Dockerfile

``` dockerfile

FROM andrius/asterisk

RUN apk add --update less psqlodbc asterisk-odbc asterisk-pgsql && \
    rm -rf /var/cache/apk/*
```

Aquí no se compila desde fuente la aplicación, pero más adelante veremos como se
puede hacer un contenedor con la apliación desde fuente.

Para crear este contenedor, necesitamos ejecutar el siguiente comando en el
directorio donde se encuentra el Dockerfile:

``` sh
docker build -t zentauro/asterisk:0.1 .
```

Una vez está creado el contenedor, podemos correr el servicio de asterisk con el
script `run.sh`:

``` sh
#!/usr/bin/env bash
set -euo pipefail

docker run -ti --rm \
    -v "${PWD}/../logs":/var/log/asterisk \
    -v "${PWD}/configs":/etc/asterisk \
    -p 5060:5060 \
    -p 8088:8088 \
    -p 5038:5038 \
    zentauro/asterisk:0.1
```

# Uso de la API AMI

En el directorio `apir_py` se encuentra una aplicación de línea de comandos que
nos permite conectarnos a la api AMI de asterisk para ver los eventos que van
ocurriendo en el servidor de forma remota.

Para usarla se tiene que especificar el host y puerto donde asterisk está
escuchando para la api y el nombre y usuario definidos para el uso de esta api.

Para poder correr esta aplicación se necesita la herramienta pipenv y se ejecuta
de la siguiente forma:

``` shell
pipenv install
pipenv shell
python main.py <resto de argumentos>
```

La parte relevante del programa en cuestión es la siguiente:
``` python
from tornado.ioloop import IOLoop
from tornado.web import Application
import asyncio
from sys import argv, exit

from apir_py.web_api import EventsWebSocket
from apir_py.asterisk_conn import ast_connect


def make_app():
    return Application([
        (r"/api", EventsWebSocket)
    ])


def print_handler(e):
    print(e)


def main():
    if len(argv) != 5:
        print(f"Usage: {argv[0]} <host> <port> <username> <secret>\n")
        exit(1)

    try:
        host = argv[1]
        port = int(argv[2])
        username = argv[3]
        secret = argv[4]
    except:
        print("Error while parsing arguments")
        exit(1)

    ast_conn = ast_connect(host, port, username, secret, print_handler)

    app = make_app()
    app.listen(8888)

    ast_conn.connect()


if __name__ == "__main__":
    main()
```
