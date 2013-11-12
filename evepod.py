import os
from eve import Eve

app = Eve()

def before_insert_data(documents):
	print "A POST to data was just performed!"
	for d in documents:
		print "Posting " + d["s"] + " data from " + d["p"] + " to the database"
		
def deploy_new_pod(request, payload):
	for d in documents:
		print "DEPLOYING a new POD, " + d["urlid"] + " !"
		# g = app.data.find_one(gateways,{"urlid":"robogateway"})
		print json.dumps(g)
		
def deploy_new_gateway(request, payload):
	for d in documents:
		print "DEPLOYING a new GATEWAY, " + d["urlid"] + " !"

# Heroku defines a $PORT environment variable that we use to determine
# if we're running locally or not.
port = os.environ.get('PORT')
if port:
    host = '0.0.0.0'
    port = int(port)
else:
    host = '0.0.0.0'
    port = 3000

# Start the application
if __name__ == '__main__':
# Adding data to the system:
	app.on_insert_data += before_insert_data
# Administering pods, gateways, and sensors:
	app.on_insert_pods += deploy_new_pod
	app.on_insert_gateways += deploy_new_gateway
# Run the program:
	app.run(host=host, port=port, debug=True)
