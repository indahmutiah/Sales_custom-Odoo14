# -*- coding: utf-8 -*-
{
    'name': "Test Inherit Sales ",

    'summary': """
        Module Inherit Sales""",

    'description': """
        For Technical Test 
    """,

    'author': "Indah Mutiah ",
    'website': "",

    'category': 'Category Modul',
    # 'sequence': -100,
    'version': '0.1',

		# Depencicy
    'depends': ['base','sale'],

		# Include ALL XML Code in Here be mindful of order
    'data': [
        # 'security/access_groups.xml',
        'views/sale_order_view.xml'
        # 'security/ir.model.access.csv',
        
        
    ],
    'installable': True,
    'application': True,

}