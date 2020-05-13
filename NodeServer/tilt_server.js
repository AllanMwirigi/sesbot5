const bodyParser = require('body-parser');
const express = require('express');
const app = express();
const jsonParser = bodyParser.json();
// app.use(express.static('public'));

async function main() {

	// const port = process.env.PORT || 3000;
	// await app.listen(port);
	await app.listen(3000, () => console.log('SESBot5 Node server listening on port 3000'))
}

main();

let currentmotion = 'S';
let rotAngle = 0;

async function onPostCommand(req, res){
    currentmotion = req.body.command;
    rotAngle = req.body.rotAngle;
    currentmotion = command;
    rotAngle = angle;
	console.log(command + '  '+ toString(rotAngle));
	let response = {
		response: "successful"
	};
	res.send(response);
}
app.post('/post', jsonParser, onPostCommand);

async function onGetCommand(req, res){

	let command = {
        currentmotion: currentmotion,
        rotAngle: rotAngle
	};
	res.send(command);

}
app.get('/get', jsonParser, onGetCommand);
