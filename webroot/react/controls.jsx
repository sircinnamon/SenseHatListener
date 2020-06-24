/* global React, forceColourChange:writable */
/* exported Controls, forceColourChange */
class Controls extends React.Component {
	constructor(props) {
		super(props)
		this.state = {}
		this.colorSelector = React.createRef()
	}

	componentDidMount() {
		forceColourChange = function () {
			//console.log("FORCECHANGE")
			this.props.setColourFn("#" + this.colorSelector.current.value)
		}.bind(this)
	}
	render() {
		let divStyle = {
			width: "80vmin",
			margin: "2vh auto",
			height: "10vmin"
		}
		let svgStyle = {
			maxHeight: "10vmin",
			maxWidth: "10vmin",
			width: "10vmin",
			margin: "0vmin 1vmin"
		}
		let brushStyle = {
			...svgStyle,
			float: "left",
			borderBottom: this.props.selectedTool == "brush" ? "1vh solid #7289DA" : "",
			borderRadius: this.props.selectedTool == "brush" ? "1vh" : ""
		}
		let eraserStyle = {
			...svgStyle,
			float: "left",
			borderTop: this.props.selectedTool == "eraser" ? "1vh solid #7289DA" : "",
			borderRadius: this.props.selectedTool == "eraser" ? "1vh" : ""
		}
		let tooltipStyle = {
			opacity: "0",
			userSelect: "none",
			width: "10vmin",
			fontSize: "3vmin",
			backgroundColor: "#43b581",
			color: "#fff",
			textAlign: "center",
			padding: "0.3vh 0",
			borderRadius: "6px",
			fontWeight: "bold",
			position: "absolute",
			zIndex: "1",
			top: "-55%",
			left: "calc(10%)",
			transition: "opacity 0.5s linear"
		}
		return (
			<div style={divStyle}>
				<svg
					style={brushStyle}
					id="brushsvg"
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 36 36"
					transform="scale(-1,1)"
					onClick={() => {
						this.props.setToolFn("brush")
					}}
				>
					<path
						fill="#99AAB5"
						d="M14.57 27.673c2.814-1.692 6.635-3.807 9.899-7.071 7.03-7.029 12.729-16.97 11.314-18.385C34.369.803 24.428 6.502 17.398 13.531c-3.265 3.265-5.379 7.085-7.071 9.899l4.243 4.243z"
					/>
					<path
						fill="#99AAB5"
						d="M.428 34.744s7.071 1.414 12.021-3.536c2.121-2.121 2.121-4.949 2.121-4.949l-2.829-2.829s-3.535.708-4.95 2.122c-1.414 1.414-2.518 4.232-2.888 5.598-.676 2.502-3.475 3.594-3.475 3.594z"
					/>
					<path
						fill="#23272A"
						d="M17.882 25.328l-5.168-5.168c-.391-.391-.958-.326-1.27.145l-1.123 1.705c-.311.471-.271 1.142.087 1.501l4.122 4.123c.358.358 1.03.397 1.501.087l1.705-1.124c.472-.311.536-.878.146-1.269z"
					/>
					<path
						fill="#7289DA"
						d="M11.229 32.26c-1.191.769-1.826.128-1.609-.609.221-.751-.12-1.648-1.237-1.414-1.117.233-1.856-.354-1.503-1.767.348-1.393-1.085-1.863-1.754-.435-.582 1.16-1.017 2.359-1.222 3.115-.677 2.503-3.476 3.595-3.476 3.595s5.988 1.184 10.801-2.485z"
					/>
				</svg>
				<button
					name="brush"
					style={{
						padding: "0px",
						border: "0px",
						backgroundColor: this.props.selectedColour,
						width: "10vmin",
						height: "10vmin",
						outline: "0px",
						userSelect: "none"
					}}
					className={
						"jscolor {width:243, height:150, borderColor:'#7289DA', insetColor:'#7289DA', backgroundColor:'#23272A', value: '" +
						this.props.selectedColour +
						"', valueElement:brushColor, onFineChange:'forceColourChange()'}"
					}
					id="brush"
				>
				</button>
				<input
					id="brushColor"
					style={{ display: "none" }}
					ref={this.colorSelector}
				/>
				<div style={{ float: "right" }}>
					<svg
						style={eraserStyle}
						id="pencilsvg"
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 36 36"
						transform="rotate(180)"
						onClick={() => {
							this.props.setToolFn("eraser")
						}}
					>
						<path
							fill="#23272A"
							d="M35.222 33.598c-.647-2.101-1.705-6.059-2.325-7.566-.501-1.216-.969-2.438-1.544-3.014-.575-.575-1.553-.53-2.143.058 0 0-2.469 1.675-3.354 2.783-1.108.882-2.785 3.357-2.785 3.357-.59.59-.635 1.567-.06 2.143.576.575 1.798 1.043 3.015 1.544 1.506.62 5.465 1.676 7.566 2.325.359.11 1.74-1.271 1.63-1.63z"
						/>
						<path
							fill="#7289DA"
							d="M13.643 5.308c1.151 1.151 1.151 3.016 0 4.167l-4.167 4.168c-1.151 1.15-3.018 1.15-4.167 0L1.141 9.475c-1.15-1.151-1.15-3.016 0-4.167l4.167-4.167c1.15-1.151 3.016-1.151 4.167 0l4.168 4.167z"
						/>
						<path
							fill="#99AAB5"
							d="M31.353 23.018l-4.17 4.17-4.163 4.165L7.392 15.726l8.335-8.334 15.626 15.626z"
						/>
						<path
							fill="#99AAB5"
							d="M32.078 34.763s2.709 1.489 3.441.757c.732-.732-.765-3.435-.765-3.435s-2.566.048-2.676 2.678z"
						/>
						<path
							fill="#23272A"
							d="M2.183 10.517l8.335-8.335 5.208 5.209-8.334 8.335z"
						/>
						<path
							fill="#99AAB5"
							d="M3.225 11.558l8.334-8.334 1.042 1.042L4.267 12.6zm2.083 2.086l8.335-8.335 1.042 1.042-8.335 8.334z"
						/>
					</svg>
					<svg
						style={svgStyle}
						id="xsvg"
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 36 36"
						onClick={() => {
							this.props.clearFn()
						}}
					>
						<path
							fill="#7289DA"
							d="M21.533 18.002L33.768 5.768c.976-.976.976-2.559 0-3.535-.977-.977-2.559-.977-3.535 0L17.998 14.467 5.764 2.233c-.976-.977-2.56-.977-3.535 0-.977.976-.977 2.559 0 3.535l12.234 12.234L2.201 30.265c-.977.977-.977 2.559 0 3.535.488.488 1.128.732 1.768.732s1.28-.244 1.768-.732l12.262-12.263 12.234 12.234c.488.488 1.128.732 1.768.732.64 0 1.279-.244 1.768-.732.976-.977.976-2.559 0-3.535L21.533 18.002z"
						/>
					</svg>
					<div
						className="submitDiv"
						style={{ position: "relative", display: "inline-block" }}
					>
						<span
							style={{
								...tooltipStyle,
								backgroundColor: "#43b581",
								opacity: this.props.showSentTooltip ? "1" : "0"
							}}
							id="sentTooltip"
							className="tooltiptext"
						>
							Sent!
							<div
								style={{
									position: "absolute",
									top: "100%",
									left: "50%",
									marginLeft: "-1vmin",
									borderWidth: "1vmin",
									borderStyle: "solid",
									borderColor: "#43b581 transparent transparent transparent",
									width: "0px"
								}}
							/>
						</span>
						<span
							style={{
								...tooltipStyle,
								backgroundColor: "#faa61a",
								opacity: this.props.showFrameTooltip ? "1" : "0"
							}}
							id="frameTooltip"
							className="tooltiptext"
						>
							Save
							<div
								style={{
									position: "absolute",
									top: "100%",
									left: "50%",
									marginLeft: "-1vmin",
									borderWidth: "1vmin",
									borderStyle: "solid",
									borderColor: "#faa61a transparent transparent transparent",
									width: "0px"
								}}
							/>
						</span>
						<svg
							style={svgStyle}
							id="arrowsvg"
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 36 36"
							onClick={() => {
								this.props.submitFn()
							}}
						>
							<path
								fill="#7289DA"
								d="M36 32c0 2.209-1.791 4-4 4H4c-2.209 0-4-1.791-4-4V4c0-2.209 1.791-4 4-4h28c2.209 0 4 1.791 4 4v28z"
							/>
							<path fill="#99AAB5" d="M7 14h9V7l13 11-13 11v-7H7z" />
						</svg>
					</div>
				</div>
			</div>
		)
	}
}
