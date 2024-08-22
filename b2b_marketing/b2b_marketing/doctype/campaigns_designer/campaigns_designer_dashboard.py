from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		# 'heatmap': True,
		# 'heatmap_message': _('This is based on transactions against this agent.'),
		'fieldname': 'campaigns_name',
		'transactions': [
			{
				'label': _('Campaigns'),
				'items': ['Campaigns']
			},{
				'label': _('Invoices'),
				'items': ['Sales Invoice']
			},
		]
	}