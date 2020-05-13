from flask import Flask, request, jsonify
import motors

app = Flask(__name__)

@app.route("/")
def home():
	# return render_template('home.html')
	return 'Hello Good sir'


@app.route("/postcommands", methods=['POST'])
def command():
	global lastmotion
	data = request.get_json()
	motion = data['command']
    angle = data['rotAngle']
	# print motion
	response = dict(response='successful')
	# return 'The command is {}'.format(motion)
	if motion == 'S':
        print 'stop'
        motors.stop()

    if motion == 'F':
        print 'forward'        
        motors.forwardTilt(angle)

    if motion == 'B':
        print 'reverse'        
        motors.reverseTilt(angle)

	return jsonify(response)
	

if __name__ == "__main__":
	app.run(host='0.0.0.0')  #make server externally accessible
	# app.run(debug=True)

