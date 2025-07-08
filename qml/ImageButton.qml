import QtQuick

Item {
	id: root

	property color bgcolor: "#333333"
	property color bcolor: "#8b13a0"
	property alias source: caption.source
	property int size: 100
	property alias widthImage: caption.width
	property alias heightImage: caption.height

	signal pressed()

	width: size
	height: size/2

	Rectangle {

		anchors.fill: parent
		radius: width/2
		color: mouseArea.containsPress? Qt.darker(root.bgcolor): root.bgcolor
		border.color: bcolor
		border.width: 2

		Image {
			id: caption
			anchors.centerIn: parent

			width: parent.width>parent.height?parent.height:parent.width
			height: parent.width>parent.height?parent.height:parent.width
		}

		MouseArea {
			id: mouseArea

			anchors.fill: parent
			hoverEnabled: false
			onClicked: root.pressed()
		}
	}


}