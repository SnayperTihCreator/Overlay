import QtQuick
import QtQuick.Window
import QtQuick.Controls

ApplicationWindow {
    id: mainWindow
    visible: true
    
    color: "transparent"
    width: Screen.width
    height: Screen.height
    flags: Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint

    Component.onCompleted: {
        Application.style = "Fusion"
        Qt.styleHints.style = "Material"
    }

    Connections {
        target: OverlayController
        function onVisibleChanged(){
            mainWindow.visible = !mainWindow.visible
        } 
    }
    

    FontLoader {
        id: marckScript
        source: "qrc:/base/fonts/MarckScript.ttf"
    }

    readonly property font mainFont: ({
        family: marckScript.name,
        pixelSize: 20,
        bold: true
    })

    Rectangle {
        id: win
        objectName: "win"
        color: "#452a2a2a"
        anchors.fill: parent
        opacity: 0.75

        Rectangle {
            id: containerListView
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            height: 600
            width: 400
            color: "#23000000"
            border.color: "#000"


            ListView {
                id: pluginsList
                anchors.fill: parent


                ScrollBar.vertical: ScrollBar {
                    anchors.right: parent.right
                    anchors.rightMargin: -20
                }

                model: OverlayController.pluginsModeData

                delegate: Rectangle {
                    height: 60
                    width: ListView.view.width
                    color: "#FF333333"
                    border.color: "black"


                    Text {
                        font: mainFont
                        anchors.centerIn: parent
                        text: model.display || ""
                        color: "#009b34"
                    }

                    Text {
                        font: mainFont
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
                        width: 32
                        height: 32
                    }
                    

                    Switch {
                        id: control
                        indicator: Image {
                            source: control.checked?"qrc:/base/icons/c_checkbox.png":"qrc:/base/icons/u_checkbox.png"
                            width: 48
                            height: 48
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        onToggled: pluginsList.model.updateStateItem(index, checked)
                    }
                }
            }
        }

        SquircleButton {
            size: 75
            text: "ESC"
            onPressed: Qt.quit()

            anchors.margins: 10
            anchors.top: parent.top
            anchors.left: parent.left

            font: mainFont
        }

        SquircleButton {
            size: 75
            text: "X"
            onPressed: mainWindow.visible = false

            anchors.margins: 10
            anchors.top: parent.top
            anchors.right: parent.right

            font: mainFont
        }

        ImageButton {
            size: 80
            source: "image://modul/root/icons/setting.png?scheme=qt&modulate=%238b13a0"

            anchors.margins: 10
            anchors.bottom: parent.bottom
            anchors.right: parent.right

            onPressed: settingWindow.visible = !settingWindow.visible
        }

        SettingWindow {
            id: settingWindow
            anchors.centerIn: parent

            model: OverlayController.settingModel

            font: mainFont
        }
        
    }        
}