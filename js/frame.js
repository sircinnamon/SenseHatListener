function Frame(board){

	this.canvas_element = function(id){
		var canvas = document.createElement("canvas")
		canvas.setAttribute("id", id);
		canvas.setAttribute("class", "frameCanvas");
		canvas.setAttribute("height", "71"); //8*8 + 1 px gap
		canvas.setAttribute("width", "71");
		return canvas;
	}

	this.display = function(canvas){
		var ctx = canvas.getContext("2d");
		for(var row = 0; row<8; row++){
			for(var col = 0; col<8; col++){
				this.display_pixel(row, col, ctx, board[row][col]);
			}
		}
	}

	this.display_pixel = function(row, col, ctx, colour){
		if(!colour){colour="#23272A"}
		ctx.fillStyle = colour;
		ctx.fillRect((col*9), (row*9), 8, 8);
	}

}