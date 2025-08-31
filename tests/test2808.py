from PySide6.QtGui import QColor


def opacity(color: QColor, value: int):
    colorHex = color.name(QColor.NameFormat.HexRgb).strip("#")
    return f"#{value:02x}{colorHex}"


print(opacity(QColor("#ff000"), 255))
