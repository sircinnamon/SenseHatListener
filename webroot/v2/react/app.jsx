class App extends React.Component {
	constructor(props){
		super(props);
		this.state = {
			boardState: [[],[],[],[],[],[],[],[]],
			boardHistory: [],
			boardHistoryStart:  [[],[],[],[],[],[],[],[]],
			frames: [],
			selectedColour: "#7289DA",
			selectedTool: "brush"
		};
	}

	render() {
		return (
			<div>
				<Board
					state={this.state.boardState}
					history={this.state.boardHistory}
					historyStart={this.state.boardHistoryStart}
					updateStateFn={((board)=>{this.setState({boardState: board})}).bind(this)}
					saveFrameFn={((frame)=>{this.setState({frames: this.state.frames.concat(frame)})}).bind(this)}
					selectedColour={this.state.selectedColour}
				/>
				<Controls
					clearFn={(()=>{this.setState({boardState: [[],[],[],[],[],[],[],[]], boardHistory: [], boardHistoryStart:  [[],[],[],[],[],[],[],[]], frames: []})}).bind(this)}
					setColourFn={((colour)=>{this.setState({selectedColour: colour})}).bind(this)}
					setToolFn={((tool)=>{this.setState({selectedTool: tool})}).bind(this)}
					submitFn={(()=>{console.log(this.state.boardState)}).bind(this)}
				/>
			</div>
		)
	}
}

class Board extends React.Component {
	constructor(props){
		super(props);
		this.state = {
		};

		this.updateCell = function(row, column){
			let b = this.props.state;
			b[row][column] = this.props.selectedColour;
			this.props.updateStateFn(b);
		}
	}

	render() {
		let rows = [];
		for (var i = 0; i < 8; i++) {
			let row = (<Row key={"row"+i} index={i} updateCellFn={this.updateCell.bind(this)} state={this.props.state[i]}/>)
			rows = rows.concat(row);
		}
		let style = {
			borderCollapse: "collapse"
		}
		return (
			<div>
				{JSON.stringify(this.props)}
				<table style={style}>
					<tbody>
						{rows}
					</tbody>
				</table>
			</div>
		)
	}
}

class Row extends React.Component {
	constructor(props){
		super(props);
		this.state = {
		};
	}

	render() {
		let cells = [];
		for (var i = 0; i < 8; i++) {
			let cell = (<Cell key={"cell"+this.props.index+"-"+i} row={this.props.index} column={i} updateCellFn={this.props.updateCellFn} state={this.props.state[i]}/>)
			cells = cells.concat(cell);
		}
		return (
			<tr>
				{cells}
			</tr>
		)
	}
}

class Cell extends React.Component {
	constructor(props){
		super(props);
		this.state = {
		};
	}

	render() {
		let bg = "";
		if(this.props.state){
			bg = hexToRgb(this.props.state);
			bg = `rgb(${bg[0]},${bg[1]},${bg[2]})`
		}
		let style = {
			height: "10px",
			width: "10px",
			border: "1px solid white",
			background: bg
		}
		return (
			<td
				onClick={()=>{this.props.updateCellFn(this.props.row, this.props.column)}}
				style={style}

			/>
		)
	}
}

class Controls extends React.Component {
	constructor(props){
		super(props);
		this.state = {
		};
	}

	render() {
		return (
			<div>
				<button
					onClick={()=>{this.props.clearFn()}}
				>
					Clear
				</button>
				<button
					onClick={()=>{this.props.submitFn()}}
				>
					Submit
				</button>
			</div>
		)
	}
}

