import QtQuick
import QtQuick.Controls

Rectangle {
	id: root
	width: 400
	height: 400
	visible: false

	property color bgcolor: "#333333"
	property var model
	property font font

	signal pressedItem(string name)

	color: bgcolor

	Text {
        font: root.font
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.margins: -40
        text: "Настройки"
        color: "#009b34"
	}

	ListView {
        anchors.left: parent.left
        anchors.margins: -125
        height: parent.height
        width: 100
        model: root.model


        delegate: Rectangle {
            width: parent.width
            height: 40
            color: "transparent"
            border.color: "#000"

            Text {
                font: root.font
                anchors.centerIn: parent
                text: model.display || ""
                color: "#009b34"
            }

            MouseArea {
            	id: mouseArea

            	anchors.fill: parent
            	onClicked: root.pressedItem(model.display)
            }
        }
    }

    StackView {
    	id: stackView
        anchors.fill: parent
        initialItem: pageCommon

        Connections {
        	target: root
        	function onPressedItem(name){
        		if (name == "WebSockets") stackView.replaceCurrentItem(pageWebSockets)
        		else if(name == "Common") stackView.replaceCurrentItem(pageCommon)
        	}
        }

    	Component {
			id: pageWebSockets

			Rectangle {
		    	color: "transparent"
		    	border.color: "#000"
		    	border.width: 1
		    	anchors.fill: stackView

		    	Column {
		    		spacing: 2
		    		anchors.fill: parent

		    		Item {		    			
		    			height: 40

		    			Text {
		    				id: textActive
						    font: root.font
						    anchors.left: parent.left
						    anchors.verticalCenter: parent.verticalCenter
						    text: "Активный"
						    color: "#009b34"
						}

						Switch {
							anchors.right: textActive.right
							anchors.verticalCenter: parent.verticalCenter
							anchors.margins: -100
							id: control
	                        indicator: Image {
	                            source: control.checked?"qrc:/base/icons/c_checkbox.png":"qrc:/base/icons/u_checkbox.png"
	                            width: 48
	                            height: 48
	                            anchors.left: parent.left
	                            anchors.verticalCenter: parent.verticalCenter
	                        }
						}
		    		}
		    	}

	    	}
		}

		Component {
			id: pageCommon

			Rectangle {
				anchors.fill: stackView
		    	color: "transparent"
		    	border.color: "#000"
		    	border.width: 1

	    	}
		}
    }
}