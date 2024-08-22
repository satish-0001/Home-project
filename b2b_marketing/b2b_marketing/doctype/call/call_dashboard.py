from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'call',
		'non_standard_fieldnames': {
			'Quality Review': 'value'
		},
		'transactions': [
			{
				'label': _('Lead'),
				'items': ['Campaign Lead','Lead Per Organization','Daily Lead']
			},
		]
	}
