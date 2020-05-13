from flask import Flask, request, jsonify
import motors

app = Flask(__name__)

@app.route("/")
def home():
	# return render_template('home.html')
	return 'Hello Good sir'

# currentmotion = 'S'
lastmotion = 'X'

@app.route("/postcommands", methods=['POST'])
def command():
	global lastmotion
	data = request.get_json()
	motion = data['command']
	# print motion
	response = dict(response='successful')
	# return 'The command is {}'.format(motion)
	if motion != lastmotion:
		lastmotion = motion
		if motion == 'S':
			print 'stop'
			motors.stop()
		elif motion == 'R':
			print 'right'
			motors.curveRight(80)
		elif motion == 'L':
			print 'left'
			motors.curveLeft(80)
		elif motion == 'F':
			print 'forward'
			motors.forward()
		elif motion == 'B':
			print 'reverse'
			motors.reverse()

	return jsonify(response)
	

if __name__ == "__main__":
	app.run(host='0.0.0.0')  #make server externally accessible
	# app.run(debug=True)

