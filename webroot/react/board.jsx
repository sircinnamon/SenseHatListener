class Board extends React.Component {
	constructor(props) {
		super(props);
		this.state = {};

		this.updateCell = function (row, column) {
			let b = this.props.state;
			if (this.props.controlHeld) {
				// Colour picker
				this.props.setColourFn(b[row][column]);
			} else if (this.props.selectedTool == "eraser" || this.props.shiftHeld) {
				this.props.updateStateFn({ x: column, y: row }, null);
			} else if (this.props.selectedTool == "brush") {
				this.props.updateStateFn({ x: column, y: row }, this.props.selectedColour);
			}
		};
	}

	render() {
		let rows = [];
		for (var i = 0; i < 8; i++) {
			let row = (
				<Row
					key={"row" + i}
					index={i}
					updateCellFn={this.updateCell.bind(this)}
					state={this.props.state[i]}
					mouseDown={this.props.mouseDown}
				/>
			);
			rows = rows.concat(row);
		}
		let tableStyle = {
			borderCollapse: "collapse",
			width: "80vmin",
			height: "80vmin",
			margin: "auto"
		};
		let divStyle = {
			boxSizing: "border-box",
			position: "relative",
			width: "84vmin",
			height: "84vmin",
			margin: "auto",
			padding: "2vmin",
			background: "#23272A"
		};
		return (
			<div style={divStyle}>
				<table style={tableStyle}>
					<tbody>{rows}</tbody>
				</table>
			</div>
		);
	}
}

class Row extends React.Component {
	constructor(props) {
		super(props);
		this.state = {};
	}

	render() {
		let cells = [];
		for (var i = 0; i < 8; i++) {
			let cell = (
				<Cell
					key={"cell" + this.props.index + "-" + i}
					row={this.props.index}
					column={i}
					updateCellFn={this.props.updateCellFn}
					state={this.props.state[i]}
					mouseDown={this.props.mouseDown}
				/>
			);
			cells = cells.concat(cell);
		}
		return <tr>{cells}</tr>;
	}
}

class Cell extends React.Component {
	constructor(props) {
		super(props);
		this.state = {};

		this.onMouseMove = function (evt) {
			if (this.props.mouseDown) {
				evt.preventDefault();
				this.onMouseDown(evt);
			}
		};

		this.onMouseDown = function (evt) {
			evt.preventDefault();
			this.props.updateCellFn(this.props.row, this.props.column);
		};
	}

	render() {
		let bg = "";
		if (this.props.state) {
			bg = hexToRgb(this.props.state);
			bg = `rgb(${bg[0]},${bg[1]},${bg[2]})`;
		}
		let style = {
			border: "2px solid #99AAB5",
			background: bg
		};
		return (
			<td
				onMouseMove={this.onMouseMove.bind(this)}
				onMouseDown={this.onMouseDown.bind(this)}
				style={style}
			/>
		);
	}
}