
#------------------------------------------------------------------------------
#
# GLOBAL SETTINGS
#
# Defines: gateway_schema, dataset_schema, pod_schema, user_schema,
#
#------------------------------------------------------------------------------
import os

# FIGURE OUT WHERE WE ARE RUNNING... ON HEROKU, OR LOCALLY?

if os.environ.get('PORT'):
	# We're hosted on Heroku! Use the MongoHQ Sandbox as our backend
	# Set API entry point (for heroku):
	# Heroku environmental variables must be set using:
	# > heroku config:set key=value
	MONGO_HOST = os.getenv('MONGO_HOST')
	MONGO_PORT = os.getenv('MONGO_PORT')
	MONGO_USERNAME = os.getenv('MONGO_USERNAME')
	MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
	MONGO_DBNAME = os.getenv('MONGO_DBNAME')
	SERVER_NAME = os.getenv('SERVER_NAME')
else:
	# Run locally, using a different port than the local gateway app
	MONGO_HOST = 'localhost'
	MONGO_PORT = 27017
	MONGO_DBNAME = 'evepod'
	SERVER_NAME = '0.0.0.0:3000'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH']

# Set the public methods for the read-only API. 
# Only authorized users can write, edit and delete
# PUBLIC_METHODS = ['GET'] 
# PUBLIC_ITEM_METHODS = ['GET']

#------------------------------------------------------------------------------
#
# RESOURCE SCHEMAS
#
# Defines: 	gateway_schema, dataset_schema, pod_schema, user_schema,
#			allsensorinfo, allpoddata, allfarmerdata, farmers 
#
#------------------------------------------------------------------------------

data_schema = {
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Note: using short variable names to save space in MongoDB.
	't':{'type':'datetime','required':True},   # datetime 
	'v':{'type':'float','required':True},      # value
	'p':{'type':'string','required':True},     # pod
	's':{'type':'string','required':True},     # sensor id (SID)
	'pod':{
		'type':'objectid',
		'data_relation': {
			'resource' :'pods',
			'field': '_id',
			'embeddable':True,
		},
	},
	'sensor':{
		'type':'objectid',
		'data_relation': {
			'resource': 'sensors',
			'field': '_id',
			'embeddable': True
		},
	}
}

user_schema = {
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for detailsself.
	# Only keys are stored on evepod. All user information is stored on stormpath
	'keys': {'type': 'list','items':[{'type':'string'}]},
}

pod_schema = { 
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Sensor text ID for use in URLs and in API data queries/submissions
	'urlid' : { # Pod URL name
		'type': 'string',
		'minlength': 1,
		'maxlength': 20,
		'required': True,
	},
	'pid' : { # Pod ID (usually phone number)
		'type':'string',
		'minlength':10,
		'maxlength':15,
		'required':True,
	},
	'imei':{ # MIEI address of cellular radio, acts as Serial Number
		'type':'string', # Need to define a MAC address type
		'unique':True,
		'required':True,
		'minlength':15,
		'maxlength':20,
	},
	'firmware':{
		'type':'integer',
		'minlength':1,
		'maxlength':1,
	},
	'status': {
		'type': 'string',
		'allowed': ['dead','deployed','provisioned','active','unknown'],
		'required':True,
	},
	'last': {
		'type':'datetime',
	},
	'owner': {
		'type':'string',
	},
	'public': {
		'type':'boolean',
		'required': True,
		'default': True
	},
	
}

sensor_schema = { 
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Sensor text ID for use in URLs and in API data queries/submissions
	'urlid' : {
		'type': 'string',
		'minlength': 1,
		'maxlength': 16,
		'required': True,
	},
	# Unique sensor ID. SID will be referenced in the PUD but should NOT be used elsewhere
	'sid' : {
		'type': 'integer',
		'minlength': 1,
		'maxlength': 3,
		'required': True,
		'unique': True,
	},
	# Number of bytes required for each piece of sensor data
	'nbytes' : {
		'type':'integer',
		'required':True,
	},
	# Format of data values, based on structs library http://docs.python.org/2/library/struct.html
	'fmt' : {
		'type':'string',
		'required':True,
		'minlength':1,
		'maxlength':1,
		'allowed': ['x','c','b','B','?','h','H','i','I','l','L','q','Q','f','d','s','p','P'],
	},
	
	
	# Byte order of data values, based on structs library http://docs.python.org/2/library/struct.html
	'byteorder' : {
		'type':'string',
		'required':False,
		'minlength':1,
		'maxlength':1,
		'allowed': ['@','=','<','>','!'],
		'default':'<',
	},
	
	# Sensor info: A text string that provides summary info for each sensor
	'info' : {
		'type':'string',
		'required':False,
		'minlength':1,
		'maxlength':256,
		'default':'no additional information is available for this sensor',
	},

	# Magnitude: A multiplier for sensor values
	'magnitude' : {
		'type':'float',
		'required':False,
		'maxlength':100,
		'default':1.0,
	},
	
	# Units: A text string that identifies the units for sensor values
	'units' : {
		'type':'string',
		'required':False,
		'maxlength':100,
	},	
	
}

#------------------------------------------------------------------------------
#
# RESOURCE DEFINITIONS
#
# Defines: pods,
#
#------------------------------------------------------------------------------
pods = {
	# 'title' tag used in item links. Defaults to the resource title minus
	# the final, plural 's' (works fine in most cases but not for 'people')
	# 'item_title': 'p',
	# by default the standard item entry point is defined as
	# '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
	# additional read-only entry point. This way consumers can also perform
	# GET requests at '/<item_title>/<urlname>/'.
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'urlid'
	},

	'datasource': {
        'projection': {	'owner': 0,
        				'firmware': 0,
        			},
     },

	# We choose to override global cache-control directives for this resource.
	'cache_control': 'max-age=10,must-revalidate',
	'cache_expires': 10,

	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'item_methods': ['GET','PATCH'],

	# Public read-only access:
#	'public_methods': ['GET'],
#    'public_item_methods': ['GET'],

	'schema': pod_schema
}

data = {
	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': data_schema	
}

users = {
	# 'title' tag used in item links. Defaults to the resource title minus
	# the final, plural 's' (works fine in most cases but not for 'people')
	# 'item_title': 'f',
	# by default the standard item entry point is defined as
	# '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
	# additional read-only entry point. This way consumers can also perform
	# GET requests at '/<item_title>/<username>/'.

	# We choose to override global cache-control directives for this resource.
	'cache_control': '',
	'cache_expires': 0,
		
	# Resource security:
	# No public methods on users
#	 'public_methods': [],
#    'public_item_methods': [],

	# Only allow superusers and admin
	# 'allowed_roles': ['superuser', 'admin'],

	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST', 'DELETE'],	
	'schema': user_schema
}

sensors = {
	# 'title' tag used in item links. Defaults to the resource title minus
	# the final, plural 's' (works fine in most cases but not for 'people')
	# 'item_title': 'f',
	# by default the standard item entry point is defined as
	# '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
	# additional read-only entry point. This way consumers can also perform
	# GET requests at '/<item_title>/<lastname>/'.
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'urlid'
	},
	# We choose to override global cache-control directives for this resource.
	'cache_control': 'max-age=10,must-revalidate',
	'cache_expires': 10,
	
	# Public read-only access:
#	'public_methods': ['GET'],
#    'public_item_methods': ['GET'],

	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': sensor_schema
}
#------------------------------------------------------------------------------
#
# DOMAINS
#
# Uses: pods, users, farmers, gateways, sensors, datasets
#
#------------------------------------------------------------------------------

DOMAIN = {
    	'pods': pods,
		'users':users,
		'sensors':sensors,
		'data':data,
}

