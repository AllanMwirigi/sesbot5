// const bodyParser = require('body-parser');
const express = require('express');
const app = express();
// const jsonParser = bodyParser.json();
// app.use(express.static('public'));

async function main() {

	// const port = process.env.PORT || 3000;
	// await app.listen(port);
	await app.listen(3000, () => console.log('RC server listening on port 3000!'))
}

main();

async function onPostCommand(req, res){
	const body = req.body;
}
app.post('/post', jsonParser, onPostCommand);