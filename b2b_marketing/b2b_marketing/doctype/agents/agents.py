# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils.nestedset import NestedSet
from erpnext import get_default_currency
from openai import OpenAI
# from pathlib import Path
# from playsound import playsound
import json
import os
from frappe import utils

class Agents(NestedSet):
	nsm_parent_field = 'parent_agents'



	def validate(self):
		if self.employee:
			if frappe.db.exists("Agents", {"employee": self.employee,'name':['!=',self.name]}):
				frappe.throw("Agent With Same Employee Already Exist")

		

		

	def onload(self):
		self.load_dashboard_info()

	def load_dashboard_info(self):
		info = {}
		company_default_currency = get_default_currency()
		# allocated_amount = frappe.db.sql("""
		# 	select sum(allocated_amount)
		# 	from `tabSales Team`
		# 	where sales_person = %s and docstatus=1 and parenttype = 'Sales Order'
		# """,(self.sales_person_name))
		info["allocated_amount"] = 0
		# info["allocated_amount"] = flt(allocated_amount[0][0]) if allocated_amount else 0
		# info["currency"] = company_default_currency
		self.set_onload('dashboard_info', info)


#----------------------------------------------------------------------------------------------------------
		
	#OpenAI Robocaller Code \/

	# Converting Text to speech
	@staticmethod
	def generate_audio(client, text, voice):
		print('generate_audio')
		path = frappe.get_site_path('public', 'files')
		# path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../sites/assets/app/sound'))
		# print('=======',path)
		# speech_file_path = Path(__file__).parent / "speech.mp3"
		speech_file_path = path+'/speech.mp3'
		print('path-------',speech_file_path)
		response = client.audio.speech.create(
			model="tts-1",
			voice=voice,
			input=text
		)
		response.stream_to_file(speech_file_path)
		# playsound(speech_file_path)
		# frappe.utils.play_sound("ping")
		return 'done'
		# return speech_file_path



	# Generating Text from OpenAI
	@staticmethod
	def generate_text(client, pat):
		response = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=pat["data"]
		)
		print(pat["data"])
		bot_response = response.choices[0].message.content
		print('bot_response----',bot_response)
		return bot_response

	# Savig Chat History
	@frappe.whitelist(allow_guest=True)
	def save_history(self,name, message):
		doc = frappe.get_doc("Chat History",name)
		pat = {
			"data":[]
		}

		current = message
		pat["data"].append(current)

		# doc.history = json.dumps(pat)

		if doc.history:
			json_data = json.loads(doc.history)
			json_data["data"].append(current)

			doc.history = json.dumps(json_data)
		else:
			doc.history = json.dumps(pat)
		# doc.insert(ignore_permissions=True)
		doc.save(ignore_permissions=True)


		json_data = json.loads(doc.history)
		# print(type(json_data['data']),json_data['data'])
		return json_data['data']


	def openai_setup_prompt(self, tag=None,prompt=None):

		#OpenAI Settings
		doc = frappe.get_doc("Open AI Setting")
		client = OpenAI(api_key=doc.openai_api_key)
		personality = self.personality
		lang = self.language
		lang_code = frappe.get_doc("Language",lang)
		lang = lang_code.language_name
		# personality =  personality +f'your name is {self.name} use this {tag} The conversation should be conducted in {lang} language ({lang_code}). {prompt} '
		sales_prompt = f"You are a sales agent named {self.name}. Your personality is {personality}. Here's your prompt:\n\n{prompt}\n\nTags: {', '.join(tag)}\nLanguage: {lang} ({lang_code}) \nWord Limit: {self.word_limit}"
 
		pat = {"data": [{"role" : "system", "content" : f"{sales_prompt}"}]}


		pat["data"].append({"role" : "user", "content" : f"Hi"})

		bot_response = self.generate_text(client, pat)
		print('bot')
		pat['data'].append({"role" : "assistant", "content" : f"{bot_response}"})
		if not frappe.db.exists("Chat History", self.name):
			chat_history = frappe.new_doc("Chat History")
			chat_history.agent = self.name
			chat_history.history = json.dumps(pat)
			chat_history.insert(ignore_permissions=True)
		else:
			print('in else condi')
			chat_history = frappe.get_doc("Chat History", self.name)
			chat_history.history = json.dumps(pat)
			chat_history.save(ignore_permissions=True)

		res = self.generate_audio(client, bot_response, self.voice_options)
		print('res---------',res)
		return res

	#Voice test------------------------------------------------------------------------
 
	@frappe.whitelist(allow_guest=True)
	def voice_test(self):

		#OpenAI Settings
		doc = frappe.get_doc("Open AI Setting")
		client = OpenAI(api_key=doc.openai_api_key)

		voice_option = self.voice_options
		lang = self.language
		lang_code = frappe.get_doc("Language",lang)
		lang = lang_code.language_name
		text = f"You are a sales agent of ERP in dexciss Technology named {self.name}, introduce yourself.In \nLanguage: {lang} ({lang_code}) within 15 words"

		pat = {"data": [{"role" : "system", "content" : f"{text}"}]}


		pat["data"].append({"role" : "user", "content" : f"Hi"})

		bot_response = self.generate_text(client, pat)
		pat['data'].append({"role" : "assistant", "content" : f"{bot_response}"})



		self.generate_audio(client,bot_response,voice_option)
		return 'done'
	
	# Intoduction and Greeting---------------------------------------------------------
 
	@frappe.whitelist(allow_guest=True)
	def intro_greeting(self):
		print('Greeting----\/')
		greet = self.greetings
		greeting = [i.greet for i in greet]
		prompt = self.greeting_prompt
		return self.openai_setup_prompt(greeting,prompt)
	
	

	#Permission ------------------------------------------------------------------------
 
	@frappe.whitelist(allow_guest=True)
	def permission(self):
		print('Permission---\/')
		persm_tags = self.permission_tags
		tags = [i.tags for i in persm_tags]
		prompt = self.permission_prompt
		return self.openai_setup_prompt(tags,prompt)


	#Problem Statement------------------------------------------------------------------
 
	@frappe.whitelist(allow_guest=True)
	def problem_statement(self):
		print('Problem Statement---\/')
		problem_tags = self.problem_statement_tags
		tags = [i.tags for i in problem_tags]
		prompt = self.problem_statement_prompt
		return self.openai_setup_prompt(tags,prompt)


	#Solution--------------------------------------------------------------------------
	
	@frappe.whitelist(allow_guest=True)
	def solution(self):
		print('Solution-------\/')
		solution_tags = self.solution_tags
		tags = [i.tags for i in solution_tags]
		prompt = self.solution_prompt
		return self.openai_setup_prompt(tags,prompt)
	
	#Follow-Up-------------------------------------------------------------------------
 
	@frappe.whitelist(allow_guest=True)
	def follow_up(self):
		print('Follow up------\/')
		follow_up_tags = self.follow_tags
		tags = [i.tags for i in follow_up_tags]
		prompt = self.follow_up_prompt
		return self.openai_setup_prompt(tags,prompt)
	

	# Chatting with AI------------------------------------------------------------------
	@frappe.whitelist(allow_guest=True)
	def start_chatting(self,input):
		lang = self.language
		lang = frappe.get_doc("Language",lang)
		lang = lang.language_name
		# print(audio)
		greeting = []
		for i in self.greetings:
			greeting.append(i.greet)
		prompt = input

		
		#OpenAI Settings
		doc = frappe.get_doc("Open AI Setting")
		client = OpenAI(api_key=doc.openai_api_key)


		hisdoc = frappe.get_doc("Chat History",self.agents_name)
		json_data = json.loads(hisdoc.history)
		name  = self.agents_name
		self.save_history(name,{"role" : "user", "content" : f"{prompt}"})
		json_data['data'].append({"role" : "user", "content" : f"{prompt}"})
		# print(messages)
		print('++++++++++++',json_data)
		bot_response = self.generate_text(client,json_data)

		self.save_history(self.agents_name,{"role" : "assistant", "content" : f"{bot_response}"})
		res = self.generate_audio(client, bot_response, self.voice_options)
		print('char-----',res)
		return res

# End 
#----------------------------------------------------------------------------------------------------------------------


def on_doctype_update():
	frappe.db.add_index("Agents", ["lft", "rgt"])


