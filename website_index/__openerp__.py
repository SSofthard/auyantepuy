# -*- coding: utf-8 -*-

{
    'name': "Sitio Web de Ayantepuy index",
    'summary': "",
    'description': """
""",
    'author': "Sofco",
    'website': "",
    'category': 'Index',
    'version': '0.1',
    'depends': ['website'],
    'data': [
        'views/templates_index.xml',
        'security/website_auyantepuy_security.xml',
        'security/group_admin_auyantepuy/ir.model.access.csv',
        'security/group_usuario_auyantepuy/ir.model.access.csv',
    ],
    'tests': [
    ],
    'installable': True,
    'application': True,
}
