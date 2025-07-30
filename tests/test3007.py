from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QGuiApplication

app = QGuiApplication([])

player = QMediaPlayer()
output = QAudioOutput()
player.setAudioOutput(output)
player.setSource("purge_siren.mp3")

player.play()

app.exec()