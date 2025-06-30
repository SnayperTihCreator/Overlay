import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: mainWindow
    width: 300
    height: 300
    visible: true
    color: "transparent"
    flags: Qt.Window | Qt.FramelessWindowHint



    // Основной прямоугольник со скругленными углами
    Rectangle {
        id: contentRect
        anchors.fill: parent
        radius: 20
        color: "#33445566"


        // Для перемещения окна
        MouseArea {
            anchors.fill: parent
            property point clickPos: "0,0"
            onPressed:{
                clickPos = Qt.point(mouse.x, mouse.y)
            }
            onPositionChanged: {
                var delta = Qt.point(mouse.x - clickPos.x, mouse.y - clickPos.y)
                mainWindow.x += delta.x
                mainWindow.y += delta.y
            }
    }


        // Кнопка закрытия (рабочий вариант)
        Rectangle {
            id: closeButton
            width: 30
            height: 30
            radius: 15
            color: mouseArea.containsMouse ? "#ff0000" : "#880000"
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 10

            Text {
                text: "X"
                anchors.centerIn: parent
                color: "white"
                font.bold: true
            }

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: Qt.quit()
            }
        }



        // Ваш основной контент
        Text {
            text: "Мое приложение"
            anchors.centerIn: parent
            font.pixelSize: 24
            color: "white"
        }
    }
}