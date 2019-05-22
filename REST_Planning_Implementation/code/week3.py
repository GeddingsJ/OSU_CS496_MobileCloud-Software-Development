from google.appengine.ext import ndb

import webapp2
import json
import datetime

class Boat(ndb.Model):
	name = ndb.StringProperty(required=True)
	idVar = ndb.StringProperty()
	boat_type = ndb.StringProperty()
	length = ndb.IntegerProperty()
	at_sea = ndb.BooleanProperty(required=True)

class Slip(ndb.Model):
	number = ndb.IntegerProperty(required=True)
	idVar = ndb.StringProperty()
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()
	
class BoatHandler(webapp2.RequestHandler):
	def patch(self, id=None):
		if id:
			key = ndb.Key(urlsafe=id).get()
			boat_data = json.loads(self.request.body)
			warning = 0
			at_sea_req = 0
			double_false = 0
			slip_dock = "abc"

			for value in boat_data:
				if value == 'name':
					ancestor_key = Boat.query().fetch()
					boat_duplicate = 0
					for boat in ancestor_key:
						if boat_data['name'] == boat.name and boat_data['name'] != key.name:
							boat_duplicate = 1
					if boat_duplicate != 1:
						key.name = boat_data['name']
					else:
						self.response.set_status(403)
						self.response.write('Duplicate entry found, identical name to existing boat, PATCH request denied\n')
						warning = 1	
				if value == 'idVar':
					self.response.set_status(403)
					self.response.write('idVar of boat cannot be changed, PATCH request denied\n')
					warning = 1				
				if value == 'boat_type':
					key.boat_type = boat_data['boat_type']
				if value == 'length':
					key.length = boat_data['length']
				if value == 'at_sea':
					if boat_data['at_sea'] == False and key.at_sea == True:
						qry = Slip.query().fetch()
						i = 0
						y = 0
						for x in qry:
							if qry[i].current_boat == "" and y == 0:
								at_sea_req = 1
								y = y + 1
								qryID = qry[i].idVar
								slip = ndb.Key(urlsafe=qryID).get()
								slip.current_boat = key.idVar

								current_time = datetime.datetime.now()
								formatted_time = str(current_time.month) + "/" + str(current_time.day) + "/" + str(current_time.year)
								slip.arrival_date = formatted_time
								
								slip_dock = slip.idVar

								slip.put()
								key.at_sea = False
							i = i + 1
						if key.at_sea != False:
							self.response.set_status(403)
							self.response.write("No slips available for placing boat, PATCH request denied")
							warning = 1
					if boat_data['at_sea'] == True and key.at_sea == False:
						qry = Slip.query().fetch()
						i = 0
						y = 0
						key.at_sea = True
						for slip in qry:
							if slip.current_boat == key.idVar:
								slip.current_boat = ""
								slip.arrival_date = ""
								slip.put()
								key.at_sea = True
					if boat_data['at_sea'] == False and key.at_sea == False:
						double_false = 1
						qry = Slip.query().fetch()
						for slip in qry:
							if slip.current_boat == key.idVar:
								slip_dock = slip.idVar

			if warning != 1:
				key.put()

				boat_dict = key.to_dict()
				boat_dict['idVar'] = "/boat/" + str(key.idVar)
				if at_sea_req == 1 or double_false == 1:
					boat_dict['dock'] = "/slip/" + str(slip_dock)

				self.response.write(json.dumps(boat_dict))

	def post(self):
		parent_key = ndb.Key(Boat, "parent_boat")
		boat_data = json.loads(self.request.body)

		ancestor_key = Boat.query().fetch()
		boat_duplicate = 0
		for boat in ancestor_key:
			if boat_data['name'] == boat.name:
				boat_duplicate = 1
		if boat_duplicate != 1:
			new_boat = Boat(name=boat_data['name'], boat_type=boat_data['boat_type'], length=boat_data['length'], at_sea=True, parent=parent_key)
			new_boat.put()

			boatID = ndb.Key(urlsafe=new_boat.key.urlsafe()).get()
			boatID.idVar = new_boat.key.urlsafe()
			boatID.put()

			boat_dict = new_boat.to_dict()
			boat_dict['idVar'] = '/boat/' + new_boat.key.urlsafe()

			self.response.write(json.dumps(boat_dict))

		else:
			self.response.set_status(403)
			self.response.write('Duplicate entry found. Please rename the boat.\n')	

	def get(self, id=None):
		if id:
			boat = ndb.Key(urlsafe=id).get()
			boat_dict = boat.to_dict()
			boat_dict['idVar'] = "/boat/" + id
			self.response.write(json.dumps(boat_dict))
		else:
			ancestor_key = Boat.query().fetch()
			for boat in ancestor_key:
				temp = boat.to_dict()
				temp['idVar'] = "/boat/" + str(boat.idVar)
				self.response.write(json.dumps(temp))
				self.response.write('\n')

	def delete(self, id=None):
		if id:
			boat = ndb.Key(urlsafe=id).get()
			qry = Slip.query().fetch()
			i = 0
			y = 0
			for x in qry:
				if qry[i].current_boat == boat.idVar and y == 0:
					qryID = qry[i].idVar
					slip = ndb.Key(urlsafe=qryID).get()
					slip.current_boat = ""
					slip.arrival_date = ""
					slip.put()
					y = 1
				i = i + 1
			boat.key.delete()

class SlipHandler(webapp2.RequestHandler):
	def patch(self, id=None):
		if id:
			key = ndb.Key(urlsafe=id).get()
			slip_data = json.loads(self.request.body)
			warning = 0

			for value in slip_data:
				if value == 'number':
					slips = Slip.query().fetch()
					slip_duplicate = 0
					for slip in slips:
						if slip_data['number'] == slip.number and slip_data['number'] != key.number:
							slip_duplicate = 1
					if slip_duplicate != 1:
						key.number = slip_data['number']
					else:
						self.response.set_status(403)
						self.response.write('Duplicate entry found, identical number to existing slip, PATCH request denied\n')
						warning = 1	
				if value == 'idVar':
					self.response.set_status(403)
					self.response.write('idVar of slip cannot be changed, PATCH request denied\n')
				if value == 'current_boat':
					boats = Boat.query().fetch()
					boat_match = 0
					for boat in boats:
						if slip_data['current_boat'] == boat.idVar and boat_match == 0:
							#permit change
							boat_match = 1
					if boat_match == 1:
						if key.current_boat != "":
							boat = ndb.Key(urlsafe=key.current_boat).get()
							boat.at_sea = True
							boat.put()

						current_time = datetime.datetime.now()
						formatted_time = str(current_time.month) + "/" + str(current_time.day) + "/" + str(current_time.year)
						key.arrival_date = formatted_time

						key.current_boat = slip_data['current_boat']
						boat = ndb.Key(urlsafe=key.current_boat).get()
						boat.at_sea = False
						boat.put()

					else:
						self.response.set_status(403)
						self.response.write('Boat requested does not exist, PATCH denied.\n')	
						warning = 1	

				if value == 'arrival_date':
					key.arrival_date = slip_data['arrival_date']

			if warning != 1:
				key.put()

				slip_dict = key.to_dict()
				slip_dict['idVar'] = "/slip/" + str(key.idVar)
				if slip_dict['current_boat'] != "" or key.current_boat == slip_dict['current_boat']:
					slip_dict['current_boat'] = "/boat/" + str(key.current_boat)

				self.response.write(json.dumps(slip_dict))

	def post(self):
		parent_key = ndb.Key(Slip, "parent_slip")

		ancestor_key = Slip.query().order(Slip.number).fetch()
		slip_counter = 0
		for slip in ancestor_key:
			if slip.number == slip_counter:
				slip_counter += 1
			else:
				break
		slip_num = slip_counter

		new_slip = Slip(number=slip_num, current_boat="", arrival_date="", parent=parent_key)
		new_slip.put()

		slipID = ndb.Key(urlsafe=new_slip.key.urlsafe()).get()
		slipID.idVar = new_slip.key.urlsafe()
		slipID.put()		

		slip_dict = new_slip.to_dict()
		temp_key = new_slip.key.urlsafe()
		slip_dict['idVar'] = '/slip/' + temp_key

		self.response.write(json.dumps(slip_dict))

	def get(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			slip_dict = slip.to_dict()
			slip_dict['idVar'] = "/slip/" + id
			if slip_dict['current_boat'] != "":
				slip_dict['current_boat'] = "/boat/" + str(slip.current_boat)
			self.response.write(json.dumps(slip_dict))
		else:
			ancestor_key = Slip.query().fetch()
			for boat in ancestor_key:
				temp = boat.to_dict()
				temp['idVar'] = "/slip/" + str(boat.idVar)
				if temp['current_boat'] != "":
					temp['current_boat'] = "/boat/" + str(boat.current_boat)
				self.response.write(json.dumps(temp))
				self.response.write('\n')
#		else:
#			ancestor_key = Slip.query().fetch()
#			for slip in ancestor_key:
#				temp = slip.to_dict()
#				temp['idVar'] = "/slip/" + str(slip.idVar)
#				if temp['current_boat'] != "":
#					temp['current_boat'] = "/boat/" + str(temp.current_boat)
#				self.response.write(json.dumps(temp))
#				self.response.write('\n')

	def delete(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			qry = Boat.query().fetch()
			if slip.current_boat != "":
				boat = ndb.Key(urlsafe=slip.current_boat).get()
				boat.at_sea = True
				boat.put()
			slip.key.delete()


# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("hello")
# [END main_page]

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/boat', BoatHandler),
	('/boat/(.*)', BoatHandler),
	('/slip', SlipHandler),
	('/slip/(.*)', SlipHandler),
], debug=True)
# [END app]