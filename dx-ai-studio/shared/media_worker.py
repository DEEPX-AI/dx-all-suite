"""Private JSON worker, executed only by a compatible media interpreter."""
import json
import sys
from pathlib import Path

import cv2
import numpy


def _image(source):
    image = cv2.imread(source)
    if image is None:
        raise ValueError(f"Cannot read image: {source}")
    return image


def _write(output, image):
    if not cv2.imwrite(output, image):
        raise OSError(f"Cannot write image: {output}")


def run(operation, data):
    if operation == "probe":
        return {"opencv": cv2.__version__, "numpy": numpy.__version__}
    if operation == "cameras":
        cameras = []
        for device in data["devices"]:
            index = int(device[len("/dev/video"):])
            camera = {"index": index, "device": device, "available": False,
                      "width": 0, "height": 0}
            capture = cv2.VideoCapture(device, cv2.CAP_V4L2)
            try:
                camera["available"] = capture.isOpened()
                if camera["available"]:
                    camera["width"] = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                    camera["height"] = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                else:
                    camera["error"] = f"Cannot open {device}; check capture support and permissions"
            finally:
                capture.release()
            cameras.append(camera)
        return {"cameras": cameras}
    if operation == "frame_count":
        capture = cv2.VideoCapture(data["source"])
        try:
            return {"count": max(0, int(capture.get(cv2.CAP_PROP_FRAME_COUNT)))}
        finally:
            capture.release()
    if operation == "thumbnail":
        image = _image(data["source"])
        height, width = image.shape[:2]
        target = int(data["width"])
        if target < 1:
            raise ValueError("Thumbnail width must be positive")
        if width > target:
            image = cv2.resize(
                image, (target, max(1, round(height * target / width))),
                interpolation=cv2.INTER_AREA,
            )
        ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if not ok:
            raise OSError("JPEG encoding failed")
        Path(data["output"]).write_bytes(encoded.tobytes())
        return {"width": image.shape[1], "height": image.shape[0]}
    if operation == "crop":
        image = _image(data["source"])
        height, width = image.shape[:2]
        if "roi" in data:
            roi = data["roi"]
            x1 = max(0, min(int(roi["x"]), width - 1))
            y1 = max(0, min(int(roi["y"]), height - 1))
            x2 = x1 + max(1, min(int(roi["w"]), width - x1))
            y2 = y1 + max(1, min(int(roi["h"]), height - y1))
        else:
            bbox = data["bbox"]
            sx, sy = width / data["display_width"], height / data["display_height"]
            x1, y1 = max(0, int(bbox[0] * sx)), max(0, int(bbox[1] * sy))
            x2, y2 = min(width, int(bbox[2] * sx)), min(height, int(bbox[3] * sy))
        if x2 <= x1 or y2 <= y1:
            return {"written": False}
        _write(data["output"], image[y1:y2, x1:x2])
        return {"written": True, "bbox": [x1, y1, x2, y2]}
    if operation == "normalize":
        source = _image(data["source"])
        image = _image(data["output"])
        ih, iw = source.shape[:2]
        rh, rw = image.shape[:2]
        source_ratio, result_ratio = iw / ih, rw / rh
        if (data["crop_panel"]
                and abs(result_ratio - source_ratio * 2) < source_ratio * 0.3):
            image = image[:, rw // 2 + 2:]
            rh, rw = image.shape[:2]
        if (rw, rh) != (iw, ih) and not (rw > iw and rh > ih):
            image = cv2.resize(image, (iw, ih), interpolation=cv2.INTER_LANCZOS4)
        _write(data["output"], image)
        return {"width": image.shape[1], "height": image.shape[0]}
    raise ValueError(f"Unknown media operation: {operation}")


if __name__ == "__main__":
    try:
        result = run(sys.argv[1], json.load(sys.stdin))
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError, cv2.error) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result))
