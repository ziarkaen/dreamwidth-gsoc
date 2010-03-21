#!/usr/bin/env python
#
#       dreamwidth2.py
#       
#       Copyright 2010  <ziarkaen@zeus>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import xmlrpclib
import hashlib
import datetime

site_url = "http://ziarkaen.hack.dreamwidth.net"

class DreamWidthSite(xmlrpclib.ServerProxy):
	def identify(self, username, password):
		"""
		Call once with username and password before using class instance.
		"""
		self.username = username
		self.password = password
		
	def call(self, short_function_name, data={}):
		"""
		Will handle all authentication - acts as layer between raw XML-RPC calls.  Always use protection.
		"""
		function_name = "LJ.XMLRPC." + short_function_name
		if not hasattr(self, function_name):
			raise Exception, "No such function: " + function_name
		info = self.authenticate()
		data.update(info)
		data.update({'ver':'0'})
		fun = getattr(self, function_name)
		return fun(data)
		
	def authenticate(self):
		"""
		Returns a dict of all authentication information, ready to be sent to another function.
		"""
		# get challenge, generate response
		question = self.LJ.XMLRPC.getchallenge()['challenge']
		password_hash = hashlib.md5(self.password).hexdigest()
		answer = hashlib.md5(question + password_hash).hexdigest()
		info = {'username':self.username, 'auth_method':'challenge', 'auth_challenge':question, 'auth_response':answer}
		return info
		
	def PostEvent(self, subject, event, security='public', allowmask=None, usejournal=None):
		"""
		Convienence function to post events.  Will automatically fill in current time.
		"""
		# dict to hold routine data
		data = {'subject':subject, 'event':event}
		# fill in local time data
		localtime = datetime.datetime.now()
		data.update({'year':localtime.year, 'mon':localtime.month, 'day':localtime.day, 'hour':localtime.hour, 'min':localtime.minute})
		# verify/fill in security info
		if security in ('public', 'private', 'usemask'):
			data['security'] = security
		else:
			raise Exception, 'Security can be one of public/private/usemask'
		if security == 'usemask':
			if not allowmask:
				raise Exception, 'Need to supply allowmask'
			data['allowmask'] = allowmask
		# check if we're posting to someone else's journal
		if usejournal:
			data['usejournal'] = usejournal
		# use self.call to auth/execute routine
		return self.call('postevent', data)
	
	def GetEvents(self):
		"""
		Not yet implemented.
		"""
		pass 

def main():
	site = DreamWidthSite(site_url + "/interface/xmlrpc")
	site.identify("dreamhackuser", "khan777")
	print site.call("getfriends")
	print site.call("getdaycounts")
	#print site.PostEvent('New function', 'This is sent from a convenience function: who wants to use the raw routines?')
	return 0

if __name__ == '__main__': main()
