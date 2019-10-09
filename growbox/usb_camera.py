#!/usr/bin/python3
import cv2
import logging

camera_logger = logging.getLogger(__name__)


class PiCamera:
    def __init__(self, port):
        self.cam = cv2.VideoCapture(port)
        self._frames = 10

    def _get_image(self):
        ret, im = self.cam.read()
        if not ret:
            raise RuntimeError("Unable to get image.")
        return im

    def capture(self, name, resize=None):
        try:
            for i in range(self._frames):
                self._get_image()
            cam_capture = self._get_image()
            if resize is not None:
                cam_capture = cv2.resize(cam_capture, resize, interpolation=1)
        except RuntimeError as err:
            camera_logger.error(err)
            camera_logger.error("Check your camera connection.")
            raise
        else:
            cv2.imwrite(name, cam_capture)

    def check_connection(self):
        return self.cam.isOpened()

    def close(self):
        self.cam.release()


if __name__ == "__main__":
    import datetime

    dt_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    img_name = "/home/pi/Pictures/" + dt_str + ".jpg"
    cam = PiCamera(0)
    try:
        cam.capture(img_name, resize=(480, 320))
    except RuntimeError:
        print("The frame is not recorded.")
    finally:
        cam.close()
