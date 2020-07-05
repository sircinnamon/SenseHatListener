/* global React */
/* exported ModeMenu */
class ModeMenu extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
		}
	}

	render() {
		let divStyle = {
			width: "84vmin",
			margin: "0.2vmin auto",
			display: "flex",
			justifyContent: "space-evenly"
		}
		return (
			<div
				style={divStyle}
			>
				<ModeMenuElement
					modeKey="map"
					setMode={this.props.setMode}
					active={this.props.currentMode=="map"}
				/>
				<ModeMenuElement
					modeKey="history"
					setMode={this.props.setMode}
					active={this.props.currentMode=="history"}
				/>
				<ModeMenuElement
					modeKey="frames"
					setMode={this.props.setMode}
					active={this.props.currentMode=="frames"}
				/>
				<ModeMenuElement
					modeKey="flash"
					setMode={this.props.setMode}
					active={this.props.currentMode=="flash"}
				/>
				<ModeMenuElement
					modeKey="spin"
					setMode={this.props.setMode}
					active={this.props.currentMode=="spin"}
				/>
				<ModeMenuElement
					modeKey="scroll"
					setMode={this.props.setMode}
					active={this.props.currentMode=="scroll"}
				/>
			</div>
		)
	}
}

ModeMenu.propTypes = {
	setMode: window.PropTypes.func,
	currentMode: window.PropTypes.string
}

class ModeMenuElement extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
		}
	}

	render() {
		let linkStyle = {
			userSelect: "none",
			fontSize: "2vmin",
			backgroundColor: (this.props.active?"#7289DA":"#23272A"),
			color: (this.props.active?"#FFF":"#99AAB5"),
			borderRadius: "6px",
			fontWeight: "bold",
			padding: "0.5vmin"
		}
		return (
			<a
				onClick={()=>{this.props.setMode(this.props.modeKey)}}
				style={linkStyle}
			>
				{this.props.modeKey}
			</a>
		)
	}
}

ModeMenuElement.propTypes = {
	modeKey: window.PropTypes.string,
	setMode: window.PropTypes.func,
	active: window.PropTypes.bool
}
