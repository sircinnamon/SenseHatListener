/* global React, format_board, format_sequence, Board, Controls, FrameList, ModeMenu */
/* exported App */
class App extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
			mode: (this.props.mode || "map"),
			boardState: [[], [], [], [], [], [], [], []],
			boardHistory: [],
			boardHistoryStart: [[], [], [], [], [], [], [], []],
			frames: [],
			selectedColour: "#7289DA",
			selectedTool: "brush",
			mouseDown: false,
			showSentTooltip: false,
			showFrameTooltip: false,
			shiftHeld: false,
			controlHeld: false,
			altHeld: false,
			frameViewerOpen: false
		}

		this.submit = function () {
			let xhr = new XMLHttpRequest()
			let url, data
			let mode = this.state.mode
			let baseUrl = "https://thor.sircinnamon.ca" //""
			// Mode set via mode url param
			if (mode == "history") {
				url = baseUrl+"/sensehat/api/sequence"
				data = JSON.stringify({
					start: format_board(this.state.boardHistoryStart),
					sequence: format_sequence(this.state.boardHistory)
				})
			} else if (mode == "string") {
				url = baseUrl+"/sensehat/api/string"
				data = JSON.stringify({ string: this.props.dataParam })
			} else if (mode == "frames") {
				url = baseUrl+"/sensehat/api/sequence"
				data = JSON.stringify({ sequence: this.state.frames })
			} else if (mode == "flash") {
				url = baseUrl+"/sensehat/api/flash"
				data = JSON.stringify({ map: format_board(this.state.boardState) })
			} else if (mode == "spin") {
				url = baseUrl+"/sensehat/api/spin"
				data = JSON.stringify({ map: format_board(this.state.boardState) })
			} else if (mode == "scroll") {
				url = baseUrl+"/sensehat/api/scroll"
				data = JSON.stringify({ map: format_board(this.state.boardState) })
			} else {
				url = baseUrl+"/sensehat/api/map"
				// url = "/sensehat/api/scroll"
				data = JSON.stringify({ map: format_board(this.state.boardState) })
			}
			if ("withCredentials" in xhr) {
				// Check if the XMLHttpRequest object has a "withCredentials" property.
				// "withCredentials" only exists on XMLHTTPRequest2 objects.
				xhr.open("POST", url, true)
			} else {
				console.log("Not supported")
				return
			}
			let that = this
			xhr.onreadystatechange = function () {
				// Call a function when the state changes.
				if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
					// Request finished. Do processing here.
					// console.log("Done")
					that.setState({ showSentTooltip: true })
					// document.getElementById("sentTooltip").style.opacity = "1"
					setTimeout(function () {
						that.setState({ showSentTooltip: false })
						// document.getElementById("sentTooltip").style.opacity = "0"
					}, 3000)
				}
			}
			xhr.send(data)
		}

		this.keyChange = function (ev, down = false) {
			if (ev.key == "Shift") {
				this.setState({ shiftHeld: down })
			} else if (ev.key == "Control") {
				this.setState({ controlHeld: down })
			} else if (ev.key == "Alt") {
				this.setState({ altHeld: down })
			} else if (ev.key == "s" && down) {
				// console.log("Save frame")
				let f = this.state.frames
				f.push({map: format_board(this.state.boardState)})
				this.setState({ frames: f, showFrameTooltip: true })
				let that=this
				setTimeout(function () {
					that.setState({ showFrameTooltip: false })
				}, 3000)
			} else if (ev.key == "S" && down) {
				// console.log("Delete frame")
				let f = this.state.frames
				f.pop()
				this.setState({ frames: f })
			} else {
				// console.log(ev.key, down)
			}
		}

		this.updateBoard = function (xy, value) {
			let b = this.state.boardState
			b[xy.y][xy.x] = value
			this.setState({ boardState: b })
			if (this.state.boardHistory.length > 0) {
				// Dont push duplicate history entries (holding mouse produces many)
				let prev = this.state.boardHistory[this.state.boardHistory.length - 1]
				if (prev && prev.x == xy.x && prev.y == xy.y && prev.colour == value) {
					return
				}
			}
			let bh = this.state.boardHistory
			let bhs = this.state.boardHistoryStart
			bh.push({ colour: value, x: xy.x, y: xy.y })
			while (bh.length > 256) {
				let px = bh.shift()
				bhs[px.y][px.x] = px.colour
			}
			this.setState({ boardHistory: bh, boardHistoryStart: bhs })
		}

		this.handleMouseDown = function(){
			this.setState({ mouseDown: true })
		}

		this.handleMouseUp = function(){
			this.setState({ mouseDown: false })
		}

		this.handleKeyDown = function(ev){
			this.keyChange(ev, true)
		}

		this.handleKeyUp = function(ev){
			this.keyChange(ev, false)
		}
	}

	componentDidMount(){
		document.addEventListener("mousedown", this.handleMouseDown.bind(this), false)
		document.addEventListener("mouseup", this.handleMouseUp.bind(this), false)
		document.addEventListener("keydown", this.handleKeyDown.bind(this), false)
		document.addEventListener("keyup", this.handleKeyUp.bind(this), false)
	}

	componentWillUnmount(){
		document.removeEventListener("mousedown", this.handleMouseDown.bind(this), false)
		document.removeEventListener("mouseup", this.handleMouseUp.bind(this), false)
		document.removeEventListener("keydown", this.handleKeyDown.bind(this), false)
		document.removeEventListener("keyup", this.handleKeyUp.bind(this), false)
	}

	render() {
		return (
			<div
				tabIndex={-1} //Need this for some reason
				style={{ border: "none", outline: "none" }}
			>
				<ModeMenu
					setMode={((m)=>{this.setState({mode: m})}).bind(this)}
					currentMode={this.state.mode}
				/>
				<Board
					state={this.state.boardState}
					updateStateFn={((xy, val) => {
						this.updateBoard(xy, val)
					}).bind(this)}
					saveFrameFn={((frame) => {
						this.setState({ frames: this.state.frames.concat(frame) })
					}).bind(this)}
					setColourFn={((colour) => {
						this.setState({ selectedColour: colour })
					}).bind(this)}
					selectedColour={this.state.selectedColour}
					selectedTool={this.state.selectedTool}
					mouseDown={this.state.mouseDown}
					shiftHeld={this.state.shiftHeld}
					controlHeld={this.state.controlHeld}
					altHeld={this.state.altHeld}
				/>
				<Controls
					clearFn={(() => {
						this.setState({
							boardState: [[], [], [], [], [], [], [], []],
							boardHistory: [],
							boardHistoryStart: [[], [], [], [], [], [], [], []],
							frames: []
						})
					}).bind(this)}
					setColourFn={((colour) => {
						this.setState({ selectedColour: colour })
					}).bind(this)}
					selectedColour={this.state.selectedColour}
					setToolFn={((tool) => {
						this.setState({ selectedTool: tool })
					}).bind(this)}
					submitFn={(() => {
						// console.log(this.state.boardState)
						this.submit()
					}).bind(this)}
					selectedTool={this.state.selectedTool}
					showSentTooltip={this.state.showSentTooltip}
					showFrameTooltip={this.state.showFrameTooltip}
				/>
				<FrameList
					hide={(this.state.mode != "frames" || (this.state.frames.length == 0))}
					isOpen={this.state.frameViewerOpen}
					frames={this.state.frames}
					updateFramesFn={((newFrames)=>{this.setState({frames: newFrames})}).bind(this)}
					toggleOpenFn={(()=>{this.setState({frameViewerOpen: !this.state.frameViewerOpen})}).bind(this)}
					setBoardStateFn={((val) => {
						this.setState({boardState: val})
					}).bind(this)}
				/>
				<div>
				</div>
			</div>
		)
	}
}

App.propTypes = {
	dataParam: window.PropTypes.string,
	mode: window.PropTypes.oneOf(["map", "history", "frames", "flash", "spin", "scroll"])
}
