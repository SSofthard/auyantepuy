# -*- coding: utf-8 -*-

{
    'name': "Sitio Web de Reserva",
    'summary': "",
    'description': """
""",
    'author': "Sofco",
    'website': "",
    'category': 'Reserva',
    'version': '0.1',
    'depends': ['website','hotel_reservation', 'toldo_reservation', 'tent','website_index','website_crm', 'website_multi_image', 'website_paquete'],
    'data': [
        
        'views/templates_reserva.xml',
        'data/reserva_data.xml',
    ],
    'tests': [
    ],
    'installable': True,
    'application': True,
}
