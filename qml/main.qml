import QtQuick
import QtQuick.Window
import QtQuick.Controls

ApplicationWindow {
    id: mainWindow
    visible: true
    
    color: "transparent"
    //opacity: 0.5
    width: Screen.width
    height: Screen.height
    flags: Qt.Window | Qt.FramelessWindowHint
    

    FontLoader {
        id: marckScript
        source: "../MarckScript-Regular.ttf"
    }

    Rectangle {
        id: win
        color: "#452a2a2a"
        anchors.fill: parent

        Rectangle {
            id: containerListView
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            height: 600
            width: 400

            ListView {
                id: pluginsList
                anchors.fill: parent

                ScrollBar.vertical: ScrollBar {
                    anchors.right: parent.right
                    anchors.rightMargin: -20
                }

                model: pluginModel

                delegate: Rectangle {
                    height: 60
                    width: ListView.view.width
                    color: "#FF333333"
                    border.color: "black"


                    Text {
                        font.family: marckScript.name
                        font.pixelSize: 20
                        font.bold: true
                        anchors.centerIn: parent
                        text: model.display || ""
                        color: "#009b34"
                    }

                    Text {
                        font.family: marckScript.name
                        font.pixelSize: 20
                        font.bold: true
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.margins: 3
                        text: model.type_plugin || ""
                        color: "#bf00e0"
                    }

                    Image {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        source: model.iconPath
                        anchors.margins: 50
                        width: 48
                        height: 48
                    }
                    

                    Switch {
                        id: control
                        indicator: Image {
                            source: control.checked?"qrc:/main/c_checkbox.png":"qrc:/main/u_checkbox.png"
                            width: 48
                            height: 48
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }
            }
        }


        Button {
            id: button1
            text: "Нажми меня"
            anchors.centerIn: parent
            onPressed: plog.log()
        }

        RoundButton {
            id: root
            text: "X"
            onClicked: Qt.quit()
        }

        
    }        
}