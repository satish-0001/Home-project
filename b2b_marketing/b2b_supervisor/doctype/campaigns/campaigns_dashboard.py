from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		# 'heatmap': True,
		# 'heatmap_message': _('This is based on transactions against this agent.'),
		'fieldname': 'campaign',
		'transactions': [
			{
				'label': _('Campaigns'),
				'items': ['Campaign Lead','Call']
			},
		]
	}