function Board(contextGrid, contextTiles) {
	this.hex_mode = false;
	this.tile_count = 0;
	this.tile_set = [];
	this.tile_size_multiplier = 1;
	this.origin = {x:null,y:null};
	this.tile_width = 60;
	this.tile_height = 60;
	this.height;
	this.width;

	this.drawBoard = function(base_x, base_y, width, height){
		var remaining_width = width;
		var remaining_height = height;
		this.origin = {x:base_x, y:base_y};
		var curr_x = base_x;
		var curr_y = base_y;
		this.tile_count=0;
		while(((base_y+height)-curr_y) >= this.tile_height+1){
			//console.log("REMAINING_Y vs CURR_Y: ",(base_y+height)-curr_y, "vs", curr_y);
			var row = [];
			while((base_x+width-curr_x) >= this.tile_width+1) {
				//console.log("REMAINING_X vs CURR_X: ",(base_x+width-curr_x), "vs", curr_x);
				var tile = new Tile(curr_x, curr_y, this.tile_height, this.tile_width, contextGrid, contextTiles);
				tile.drawTile();
				row.push(tile);
				curr_x+=this.tile_width;
				this.tile_count++;
			}	
			remaining_width = width;
			curr_x = base_x;
			this.tile_set.push(row);
			curr_y += this.tile_height;
		}
		this.width = this.tile_set[0].length * this.tile_width;
		this.height = this.tile_set.length * this.tile_height;
	}

	this.getXYByCoord = function(x,y){
		x = x - this.origin.x;
		y = y - this.origin.y;
		if(y < 0){return null;}
		if(x < 0){return null;}
		x = (x - (x % this.tile_width))/this.tile_width;
		y = (y - (y % this.tile_height))/this.tile_height;
		if(y >= this.tile_set.length){return null;}
		if(x >= this.tile_set[0].length){return null;}
		return {y:y, x:x};
	}

	this.getTileByCoord = function(x,y){
		x = x - this.origin.x;
		y = y - this.origin.y;
		if(y < 0){return null;}
		if(x < 0){return null;}
		x = (x - (x % this.tile_width))/this.tile_width;
		y = (y - (y % this.tile_height))/this.tile_height;
		if(y >= this.tile_set.length){return null;}
		if(x >= this.tile_set[0].length){return null;}
		return this.tile_set[y][x];
	}

	this.getRowByCoord = function(y){
		y = y - this.origin.y;
		if(y < 0){return null;}
		y = (y - (y % this.tile_height))/this.tile_height;
		if(y >= this.tile_set.length){return null;}
		return y;
	}

	this.getColByCoord = function(x){
		x = x - this.origin.x;
		if(x < 0){return null;}
		x = (x - (x % this.tile_width))/this.tile_width;
		if(x >= this.tile_set[0].length){return null;}
		return x;
	}

	this.clearTiles = function(){
		for(i = 0; i < this.tile_set.length; i++){
			for (var j = 0; j < this.tile_set[i].length; j++) {
				this.tile_set[i][j].clearTile();
			}
		}
	}

	this.refresh = function(position){
		for(i = 0; i < this.tile_set.length; i++){
			for (var j = 0; j < this.tile_set[i].length; j++) {
				this.tile_set[i][j].drawTile();
			}
		}
	}

}

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
var eraseMode = false;

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
}

function getColour(){
	return document.getElementById("brush").value;
}

function paintTile(tile, xy){
	var colour = getColour()
	if(eraseMode){
		tile.clearTile()
		delete boardState[xy.y][xy.x];
		return
	}
	tile.fillTile(fillStyle=colour)
	boardState[xy.y][xy.x] = colour;
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
			paintTile(board.getTileByCoord(mousePos.x, mousePos.y), board.getXYByCoord(mousePos.x, mousePos.y))
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
			setTimeout(function(){document.getElementById("sentTooltip").style.opacity = "0";}, 3000);
		}
	}
	xhr.send(JSON.stringify({board:format_board(boardState)}));
}

function format_board(board){
	output_board = [];
	for (var i = 0; i < 8; i++) {
		for (var j = 0; j < 8; j++) {
			if(!board[i][j]){
				output_board[i*8 + j] = [0,0,0]
			} else {
				output_board[i*8 + j] = hexToRgb(board[i][j])
			}
		}
	}
	return output_board
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


first_load();

window.addEventListener('mouseup', mouseup_global, {passive:false});
window.addEventListener('mousedown', mousedown_global, {passive:false});

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

function Tile(x, y, height, width, contextGrid, contextTile){
	this.is_hex = false;
	this.entity;
	this.has_caster = false;
	this.isHit = false;
	this.tile_corners = [{"x":x,"y":y},{"x":x+width,"y":y},{"x":x+width,"y":y+height},{"x":x,"y":y+height}]
	this.currentFill = null;
	this.gridColor = "#99AAB5";
	this.lineWidth = 3;

	this.drawTile = function(){
		contextGrid.beginPath();
		//0.5 because it marks the center of the 1px wide line
		contextGrid.moveTo(0.5 + this.tile_corners[0].x, 0.5 + this.tile_corners[0].y);
		contextGrid.lineTo(0.5 + this.tile_corners[1].x, 0.5 + this.tile_corners[1].y);
		contextGrid.lineTo(0.5 + this.tile_corners[2].x, 0.5 + this.tile_corners[2].y);
		contextGrid.lineTo(0.5 + this.tile_corners[3].x, 0.5 + this.tile_corners[3].y);
		contextGrid.lineTo(0.5 + this.tile_corners[0].x, 0.5 + this.tile_corners[0].y);

		contextGrid.strokeStyle = this.gridColor;
		contextGrid.lineWidth = this.lineWidth;
		contextGrid.stroke();
	}

	this.fillTile = function(fillStyle="red"){
		this.currentFill = fillStyle;
		contextTile.beginPath();
		contextTile.rect(x+1, y+1, width-1, height-1);
		contextTile.fillStyle= fillStyle;
		contextTile.fill();
	}

	this.clearTile = function(){
		this.currentFill = null;
		contextTile.clearRect(x+1, y+1, width-1, height-1);
	}

}
