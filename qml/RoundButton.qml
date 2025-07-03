import QtQuick


Item {
        id: root
        property int size: 100
        property color color: "#f00"
        property alias text: caption.text


        signal clicked()

        width: size
        height: size


        Rectangle {
            
            anchors.fill: parent
            radius: size/2
            color: mouseArea.containsPress? Qt.darker(root.color): root.color
            Text {
                id: caption
                anchors.centerIn: parent
                text: qsTr("ClickMe")
            }


            MouseArea {
                id: mouseArea
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: false
                onClicked: root.clicked()
            }
            
        }

        
    }