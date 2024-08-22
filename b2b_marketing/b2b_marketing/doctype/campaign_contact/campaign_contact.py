# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe.model.document import Document
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

class CampaignContact(Document):
	def before_save(self):
		if self.country and self.state:
			
			geolocator = Nominatim(user_agent="timezone_locator")
			location = geolocator.geocode(f"{self.state}, {self.country}")
			if location is None:
				return None
			tf = TimezoneFinder()
			timezone_str = tf.timezone_at(lat=location.latitude, lng=location.longitude)
			if timezone_str is None:
				return None
			if timezone_str:
				self.timezone = timezone_str


