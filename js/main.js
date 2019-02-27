// Box width
var bw;
// Box height
var bh;
// Mouse currently up or down
var mousedown = false;
//Current active touches
var ongoingTouches = 0;
//Long Press settings
var longPressTimer;
var longPressOrigin;
var LONG_PRESS_FORGIVENESS = 5;
var LONG_PRESS_VIBRATION = [75];

var canvasDiv = document.getElementById("canvasDiv");
var canvasGrid = document.getElementById("canvasGrid");
var contextGrid = canvasGrid.getContext("2d");
var canvasColours = document.getElementById("canvasColours");
var contextColours = canvasColours.getContext("2d");

var board;
var boardState = [[],[],[],[],[],[],[],[]];
var boardHistory = [];
var boardHistoryStart = [[],[],[],[],[],[],[],[]];
var frames = [];
var eraseMode = false;
var mode = getParameterByName("mode");

function getMousePos(canvasGrid, event) {
	var rect = canvasGrid.getBoundingClientRect();
	if(event.touches){event = event.touches[0];}
	return {
		x: event.clientX - rect.left,
		y: event.clientY - rect.top
	};
}

function resizeCanvas(canvas, width, height) {
	canvas.width = width;
	canvas.height = height;
}

function vibrate(events){
	navigator.vibrate = navigator.vibrate || navigator.webkitVibrate || navigator.mozVibrate || navigator.msVibrate;
	//console.log(navigator.vibrate);
	if (navigator.vibrate) {
		navigator.vibrate(...events);
	}
}

function clearAll(){
	board.clearTiles();
	boardState = [[],[],[],[],[],[],[],[]];
	boardHistory = [];
	boardHistoryStart = [[],[],[],[],[],[],[],[]];
	frames = [];
}

function getColour(){
	return "#"+document.getElementById("brushColor").value;
}

function paintTile(tile, xy){
	var colour = getColour()
	if(eraseMode){
		tile.clearTile()
		delete boardState[xy.y][xy.x];
		historyUpdate(xy, "#000000");
		return
	}
	tile.fillTile(fillStyle=colour)
	boardState[xy.y][xy.x] = colour;
	historyUpdate(xy, colour);
}

function historyUpdate(xy, colour){
	// Dont push duplicate history entries (holding mouse produces many)
	prev = boardHistory[boardHistory.length-1]
	if(prev && prev.x == xy.x && prev.y == xy.y && prev.colour == colour){
		return;
	}
	boardHistory.push({colour:colour, x:xy.x, y:xy.y})
	while(boardHistory.length > 256){
		var px = boardHistory.shift()
		boardHistoryStart[px.y][px.x] = px.colour;
	}
}

function save_frame(){
	document.getElementById("frameTooltip").style.opacity = "1";
	setTimeout(function(){
		document.getElementById("frameTooltip").style.opacity = "0";
	}, 1000);
	frames.push({map: format_board(boardState)});
}

function copy_colour(evt){
	var mousePos = getMousePos(canvasGrid, evt);
	var fill = board.getTileByCoord(mousePos.x, mousePos.y).currentFill
	if(fill==null){return;}
	document.getElementById("brush").jscolor.fromString(fill)
}

function mousedown_global(evt) {
	mousedown = true;
}

function mouseup_global(evt) {
	evt.preventDefault();
	mousedown = false;
}


function mousedown_func(evt) {
	evt.preventDefault();
	mousedown = true;
	var mousePos = getMousePos(canvasGrid, evt);
	mousemove_func(evt);
}

function mousemove_func(evt) {
	evt.preventDefault();
	if(mousedown){
		var mousePos = getMousePos(canvasGrid, evt);
		var tile = board.getTileByCoord(mousePos.x, mousePos.y)
		if(tile){
			if(evt.ctrlKey){
				copy_colour(evt);
			} else if(evt.shiftKey) {
				var eraseState = eraseMode;
				eraseMode = true;
				paintTile(board.getTileByCoord(mousePos.x, mousePos.y), board.getXYByCoord(mousePos.x, mousePos.y))
				eraseMode = eraseState;
			} else {
				paintTile(board.getTileByCoord(mousePos.x, mousePos.y), board.getXYByCoord(mousePos.x, mousePos.y))
			}
		}
	}
}

function mouseup_func(evt) {
	evt.preventDefault();
	mousedown = false;
}

function dblclick_func(evt) {
	evt.preventDefault();
	var mousePos = getMousePos(canvasGrid, evt);
}

function touchstart_func(evt) {
	ongoingTouches += evt.changedTouches.length;
	if(ongoingTouches == 1){
		//Start longpress
		longPressOrigin = {x:evt.touches[0].clientX, y:evt.touches[0].clientY};
		longPressTimer = setTimeout(function() {
			vibrate(LONG_PRESS_VIBRATION);
			dblclick_func(evt);
		}, 500);

		mousedown_func(evt);
	} else {
		clearTimeout(longPressTimer);
	}
}

function touchmove_func(evt) {
	if(ongoingTouches == 1){
		//Cancel longpress if in progress & have moved enough away
		if(longPressOrigin){
			var dx = evt.touches[0].clientX - longPressOrigin.x
			var dy = evt.touches[0].clientY - longPressOrigin.y
			if(Math.sqrt(dx * dx + dy * dy) > LONG_PRESS_FORGIVENESS){
				clearTimeout(longPressTimer);
				longPressOrigin = null;
			}
		}

		mousemove_func(evt);
	}
}

function touchend_func(evt) {
	ongoingTouches -= evt.changedTouches.length;
	if(ongoingTouches <= 1){
		//Cancel longpress happening
		clearTimeout(longPressTimer);
		longPressOrigin = null;

		mouseup_func(evt);
	}
}

function resize_func(evt) {
	clearTimeout(resizeTimer);
	//console.log("resize event fired");
	var resizeTimer = setTimeout(function() {
		//console.log("resize event processed");
		init_canvases();
	}, 200);
}

function keydown_func(evt){
	if(evt.keyCode==83){ // key = s
		save_frame();
	}
	var codeComplete = secretCode(evt.keyCode)
	if (codeComplete){
		console.log("Sequence Complete!");
		midi = new Audio("secret.mp3");
		midi.volume = 0.3;
		midi.loop = true;
		midi.play();
	}
}

function init_canvases() {
	bw = parseInt(getComputedStyle(canvasDiv, null).getPropertyValue("width").replace("px", ""));
	bh = parseInt(getComputedStyle(canvasDiv, null).getPropertyValue("height").replace("px", ""));

	resizeCanvas(canvasGrid, bw, bh);
	resizeCanvas(canvasColours, bw, bh);

	var tileSizeRatio = 1;
	var tileOffset = {x:0, y:0};
	board = new Board(contextGrid, contextColours);
	board.tile_width = Math.floor(Math.min(bw, bh)/8)-1
	board.tile_height = board.tile_width
	board.drawBoard(Math.floor(((bw-1)-(board.tile_width*8))/2), 0, (board.tile_width*8)+1, (board.tile_width*8)+1);

}

function first_load() {
	init_canvases();
}

function clear_state(){
	init_canvases();
}

function set_erase_mode(val){
	eraseMode = val;
	if(eraseMode){
		document.getElementById("brushsvg").classList.remove("active");
		document.getElementById("pencilsvg").classList.add("active");
	} else {
		document.getElementById("pencilsvg").classList.remove("active");
		document.getElementById("brushsvg").classList.add("active");
	}
}

function submit(){
	var xhr = new XMLHttpRequest();
	if ("withCredentials" in xhr) {
		// Check if the XMLHttpRequest object has a "withCredentials" property.
		// "withCredentials" only exists on XMLHTTPRequest2 objects.
		xhr.open("POST", "/post/", true);
	} else if (typeof XDomainRequest != "undefined") {
		// Otherwise, check if XDomainRequest.
		// XDomainRequest only exists in IE, and is IE's way of making CORS requests.
		xhr = new XDomainRequest();
		xhr.open("POST", "/post/", true);
	} else {
		return;
		console.log("Not supported")
	}

	xhr.onreadystatechange = function() { // Call a function when the state changes.
		if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
			// Request finished. Do processing here.
			// console.log("Done")
			document.getElementById("sentTooltip").style.opacity = "1";
			setTimeout(function(){
				document.getElementById("sentTooltip").style.opacity = "0";
			}, 3000);
		}
	}
	// Mode set via mode url param
	if(mode=="history"){
		xhr.send(JSON.stringify({start:format_board(boardHistoryStart),sequence:format_sequence(boardHistory)}));
	} else if(mode=="string") {
		xhr.send(JSON.stringify({string:getParameterByName("data")}));
	} else if(mode=="frames") {
		xhr.send(JSON.stringify({sequence:frames}));
	} else if(mode=="flash") {
		xhr.send(JSON.stringify({flash:format_board(boardState)}));
	} else if(mode=="spin") {
		xhr.send(JSON.stringify({spin:format_board(boardState)}));
	} else if(mode=="scroll") {
		xhr.send(JSON.stringify({scroll:format_board(boardState)}));
	} else {
		xhr.send(JSON.stringify({map:format_board(boardState)}));
	}
}

function format_board(board){
	output_board = [];
	var filled_len = 7;
	while(filled_len>=0 && board[filled_len].length==0){filled_len--;}
	for (var i = 0; i <= filled_len; i++) {
		output_board[i]=[];
		for (var j = 0; j < board[i].length; j++) {
			if(!board[i][j]){
				output_board[i][j] = []
			} else {
				output_board[i][j] = hexToRgb(board[i][j])
			}
		}
	}
	return output_board
}

function format_sequence(sequence){
	new_seq = []
	for (var i = 0; i < sequence.length; i++) {
		new_seq.push({x:sequence[i].x, y: sequence[i].y, colour:hexToRgb(sequence[i].colour)})
	}
	return new_seq
}

function hexToRgb(hex) {
	var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
	return result ? [
		parseInt(result[1], 16),
		parseInt(result[2], 16),
		parseInt(result[3], 16)
	] : null;
}

var currentLoc = 0;
function secretCode(keycode){
	var allowedKeys = {
		37: 'left',
		38: 'up',
		39: 'right',
		40: 'down',
		65: 'a',
		66: 'b'
	};
	var sequence = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b', 'a'];
	if (sequence[currentLoc] == allowedKeys[keycode]) {
		currentLoc++;
	} else if(sequence[0] == allowedKeys[keycode]) {
		//restart sequence
		currentLoc = 1;
	} else {
		currentLoc = 0;
	}
	if (currentLoc == sequence.length){
		currentLoc = 0;
		return true;
	} else {
		return false;
	}
}

function getParameterByName(name, url) {
	if (!url) url = window.location.href;
	name = name.replace(/[\[\]]/g, "\\$&");
	var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
		results = regex.exec(url);
	if (!results) return null;
	if (!results[2]) return '';
	return decodeURIComponent(results[2].replace(/\+/g, " "));
}

first_load();

window.addEventListener('mouseup', mouseup_global, {passive:false});
document.querySelector('main').addEventListener('mousedown', mousedown_global, {passive:false});

canvasGrid.addEventListener('mousedown', mousedown_func, {passive:false});
canvasGrid.addEventListener('touchstart', touchstart_func, {passive:false});
canvasGrid.addEventListener('mousemove', mousemove_func, {passive:false});
canvasGrid.addEventListener('touchmove', touchmove_func, {passive:false});
canvasGrid.addEventListener('mouseup', mouseup_func, {passive:false});
canvasGrid.addEventListener('touchend', touchend_func, {passive:false});
canvasGrid.addEventListener('touchcancel', touchend_func, {passive:false});
canvasGrid.addEventListener('dblclick', dblclick_func, {passive:false});
window.addEventListener('keydown', keydown_func, {passive:false});
document.defaultView.addEventListener('resize', resize_func, {passive:true});

document.getElementById("brushsvg").addEventListener('click', function(){set_erase_mode(false)}, {passive:true});
document.getElementById("brush").addEventListener('click', function(){set_erase_mode(false)}, {passive:true});
document.getElementById("pencilsvg").addEventListener('click', function(){set_erase_mode(!eraseMode)}, {passive:true});
document.getElementById("xsvg").addEventListener('click', clearAll, {passive:true});
document.getElementById("arrowsvg").addEventListener('click', submit, {passive:true});
