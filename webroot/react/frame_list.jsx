/* global React, rgbToHex */
/* exported FrameList */
class FrameList extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
		}

		this.moveFrame = function(index, shift){
			// console.log("Move", index, shift)
			let newFrames = [...this.props.frames]
			let movedFrame = newFrames.splice(index, 1)[0]
			newFrames.splice(index+shift, 0, movedFrame)
			this.props.updateFramesFn(newFrames)
		}

		this.removeFrame = function(index){
			// console.log("Remove", index)
			let newFrames = [...this.props.frames]
			newFrames.splice(index, 1)
			this.props.updateFramesFn(newFrames)
		}

		this.duplicateFrame = function(index){
			// console.log("Dupe", index)
			let frame = this.props.frames[index].map
			let newBoard = [[], [], [], [], [], [], [], []]
			for (let i = 0; i < frame.length; i++) {
				for (let j = 0; j < frame[i].length; j++) {
					if(frame[i][j].length == 3){newBoard[i][j] = rgbToHex(frame[i][j])}
				}
			}
			this.props.setBoardStateFn(newBoard)
		}
	}

	render() {
		let popoutStyle = {
			width: (this.props.isOpen?"11vw":"0vw"),
			height: "100vh",
			background: "#2C2F33",
			position: "absolute",
			top: "0px",
			left: "0px",
			borderRight: "3px solid  #7289DA",
			zIndex: 10,
			overflowY: "auto",
			overflowX: "hidden",
			transition: "width 0.5s"
		}
		let toggleStyle = {
			left: popoutStyle.width,
			height: "10vh",
			width: "2vw",
			background: "#7289DA",
			position: "absolute",
			top: "45vh",
			color: "#23272A",
			lineHeight: "10vh",
			fontSize: "2vw",
			zIndex: 11,
			borderRadius: "0vw 2vw 2vw 0vw",
			textAlign: "center",
			fontWeight: "bold",
			transition: "left 0.5s"
		}
		let frames = []
		for (let i = 0; i < this.props.frames.length; i++) {
			let frame = (
				<Frame
					map={this.props.frames[i].map}
					key={i}
					dupeFn={()=>{this.duplicateFrame(i)}}
					deleteFn={()=>{this.removeFrame(i)}}
					moveFn={(shift)=>{this.moveFrame(i, shift)}}
				/>
			)
			frames = frames.concat(frame)
		}
		return (
			<div>
				<div style={popoutStyle}>
					{frames}
				</div>
				<div style={toggleStyle} onClick={this.props.toggleOpenFn}>
					{this.props.isOpen?"<":">"}
				</div>
			</div>
		)
	}
}

FrameList.propTypes = {
	isOpen: window.PropTypes.bool,
	frames: window.PropTypes.array,
	updateFramesFn: window.PropTypes.func,
	toggleOpenFn: window.PropTypes.func,
	setBoardStateFn: window.PropTypes.func
}

class Frame extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
		}
		this.cellColour = function(x, y){
			if(!this.props.map){return undefined}
			if(!this.props.map[y]){return undefined}
			if(!this.props.map[y][x]){return undefined}
			if(this.props.map[y][x].length == 0){return undefined}
			let bg = this.props.map[y][x]
			return `rgb(${bg[0]},${bg[1]},${bg[2]})`
		}
	}

	render() {
		let frameStyle={
			width: "9vw",
			height: "11vw",
			margin: "0.5vw",
			background: "#23272A",
			padding: "0.5vw",
			color: "#99AAB5",
			textAlign: "right",
			fontSize: "2vw"
		}
		let tableStyle = {
			width: frameStyle.width,
			height: frameStyle.width,
			borderCollapse: "collapse"
		}
		let cellStyle = {
			border: "1px solid #99AAB5"
		}
		let buttonStyle = {
			padding: "3px",
			userSelect: "none"
		}
		let rows = []
		for (var i = 0; i < 8; i++) {
			let cells = []
			for (var j = 0; j < 8; j++) {
				let bg = this.cellColour(j, i)
				let cell = (
					<td
						style={{
							background: bg || "unset",
							...cellStyle
						}}
						key={j}
					>
					</td>
				)
				cells = cells.concat(cell)
			}
			let row = (
				<tr key={i} >{cells}</tr>
			)
			rows = rows.concat(row)
		}
		return (
			<div style={frameStyle}>
				<div>
					<table style={tableStyle}>
						<tbody>{rows}</tbody>
					</table>
					<div>
						<label style={buttonStyle} onClick={()=>{this.props.moveFn(-1)}}>&#8593;</label>
						<label style={buttonStyle} onClick={()=>{this.props.moveFn(1)}}>&#8595;</label>
						<label style={buttonStyle} onClick={()=>{this.props.deleteFn()}}>&times;</label>
						<label style={buttonStyle} onClick={()=>{this.props.dupeFn()}}>&#x2398;</label>
					</div>
				</div>
			</div>
		)
	}
}

Frame.propTypes = {
	map: window.PropTypes.array,
	dupeFn: window.PropTypes.func,
	moveFn: window.PropTypes.func,
	deleteFn: window.PropTypes.func
}
