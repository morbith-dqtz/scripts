OcaMaint
========

Script python para mantener los módulos de OCA, del proyecto ODOO, sincronizados con una instancia de base de datos.

Se encarga de descargar y/o actualizar los módulos definidos en repos.ini, los cuales podemos activar y desactivar (1/0).
Una vez tenemos los módulos disponibles y actualizados, crea enlaces simólicos y chequea los requisitos e instala, 
tando de otros repositorios de OCA, como de los módulos de python necesarios.

Si encuentra un módulo OCA que no tenemos definido, lo añade automáticamente a la configuración. 

Los requisitos python se instalan con la flag --user, así que es comnveniente correr el script con el usuario que ejecute ODOO


----

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

http://odoo-community.org/

