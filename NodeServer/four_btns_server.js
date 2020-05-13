const bodyParser = require('body-parser');
const express = require('express');
const app = express();
const jsonParser = bodyParser.json();
// app.use(express.static('public'));

async function main() {

	// const port = process.env.PORT || 3000;
	// await app.listen(port);
	await app.listen(3000, () => console.log('Pi RC server listening on port 3000'))
}

main();

let currentmotion = 'S';

async function onPostCommand(req, res){
	const command = req.body.command;
	currentmotion = command;
	console.log(command);
	let response = {
		response: "successful"
	};
	res.send(response);
}
app.post('/post', jsonParser, onPostCommand);

async function onGetCommand(req, res){

	let command = {
		currentmotion: currentmotion
	};
	res.send(command);

}
app.get('/get', jsonParser, onGetCommand);
