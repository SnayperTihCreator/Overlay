import cv3

with cv3.Video(0) as cap:
    frame = next(cap)
    cv3.imwrite("photo.jpg", frame)
    