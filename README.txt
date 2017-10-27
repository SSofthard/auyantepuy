Pasos para la implantacion del sistema:
1-instalar el archivo .deb de odoo
2-sustituir los modulos de addons contenidos (website,website_crm,website_sale) en la direccion: usr/lib/python2.7/dist-packages/openerp/addons
3-crear base de datos desde la consola para el usuario o del servicio de odoo (odoo)
4-importar la base de datos ejecutando en la consola: psql -U username -W -h host basename < basename.sql
5-cambiar los puertos del servicio de odoo
6-restaurar el servicio
7-ingresar desde el navegador a la ruta dominio del sistema
