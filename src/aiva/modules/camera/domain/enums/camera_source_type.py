from enum import StrEnum


class CameraSourceType(StrEnum):
    RTSP = "rtsp"
    RTMP = "rtmp"
    HTTP = "http"
    HLS = "hls"
    FILE = "file"
