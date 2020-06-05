function getParameterByName(name, url) {
	if (!url) url = window.location.href;
	name = name.replace(/[\[\]]/g, "\\$&");
	var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
		results = regex.exec(url);
	if (!results) return null;
	if (!results[2]) return '';
	return decodeURIComponent(results[2].replace(/\+/g, " "));
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
		new_seq.push({pixel:{x:sequence[i].x, y: sequence[i].y, colour:hexToRgb(sequence[i].colour)}})
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