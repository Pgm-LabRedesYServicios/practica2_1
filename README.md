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

# Jueves 18 marzo 2021:

# Jueves 1 abril 2021:

# Jueves 8 abril 2021:
Configuracion de agentes

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

Con estos cambios, los servicios quedan de tal forma:

Extensión | Servicio
----------|---------
7000 | Inicio de sesión como agente
7001 | Poner número para antender llamadas en la cola
7002 | Dejar de atender llamadas en la cola

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
    
