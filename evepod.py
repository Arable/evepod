import os
from eve import Eve

app = Eve()

def before_insert_data(documents):
	print "A POST to data was just performed!"
	for d in documents:
		print "Posting " + d["s"] + " data from " + d["p"] + " to the database"

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
# Run the program:
	app.run(host=host, port=port, debug=True)
