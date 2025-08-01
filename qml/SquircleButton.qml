import QtQuick

Item {
	id: root

	property color fgcolor: "#bf00e0"
	property color bgcolor: "#333333"
	property color bcolor: "#8b13a0"
	property alias text: caption.text
	property int size: 100
	property alias font: caption.font

	signal pressed()

	width: size
	height: size/2

	Rectangle {

		anchors.fill: parent
		radius: width/2
		color: mouseArea.containsPress? Qt.darker(root.bgcolor): root.bgcolor
		border.color: bcolor
		border.width: 2

		Text {
			id: caption

			color: fgcolor
			anchors.centerIn: parent
			font.pixelSize: 16
			text: "Click"
		}

		MouseArea {
			id: mouseArea

			anchors.fill: parent
			hoverEnabled: false
			onClicked: root.pressed()
		}
	}


}