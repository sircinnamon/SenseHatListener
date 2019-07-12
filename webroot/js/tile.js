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
