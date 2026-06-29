import numpy as np
import cv2
import argparse
import math
from pathlib import Path

module_dir = Path(__file__).resolve().parent



def get_rotate_crop_image(img, points):
    """
    img_height, img_width = img.shape[0:2]
    left = int(np.min(points[:, 0]))
    right = int(np.max(points[:, 0]))
    top = int(np.min(points[:, 1]))
    bottom = int(np.max(points[:, 1]))
    img_crop = img[top:bottom, left:right, :].copy()
    points[:, 0] = points[:, 0] - left
    points[:, 1] = points[:, 1] - top
    """
    assert len(points) == 4, "shape of points must be 4*2"
    img_crop_width = int(max(np.linalg.norm(points[0] - points[1]), np.linalg.norm(points[2] - points[3])))
    img_crop_height = int(max(np.linalg.norm(points[0] - points[3]), np.linalg.norm(points[1] - points[2])))
    pts_std = np.float32(
        [
            [0, 0],
            [img_crop_width, 0],
            [img_crop_width, img_crop_height],
            [0, img_crop_height],
        ]
    )
    M = cv2.getPerspectiveTransform(points, pts_std)
    dst_img = cv2.warpPerspective(
        img,
        M,
        (img_crop_width, img_crop_height),
        borderMode=cv2.BORDER_REPLICATE,
        flags=cv2.INTER_CUBIC,
    )
    return dst_img


def get_minarea_rect_crop(img, points):
    bounding_box = cv2.minAreaRect(np.array(points).astype(np.int32))
    points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

    index_a, index_b, index_c, index_d = 0, 1, 2, 3
    if points[1][1] > points[0][1]:
        index_a = 0
        index_d = 1
    else:
        index_a = 1
        index_d = 0
    if points[3][1] > points[2][1]:
        index_b = 2
        index_c = 3
    else:
        index_b = 3
        index_c = 2

    box = [points[index_a], points[index_b], points[index_c], points[index_d]]
    crop_img = get_rotate_crop_image(img, np.array(box))
    return crop_img


def get_minarea_rect(points):
    points = np.array(points, dtype=np.float32)
    bounding_box = cv2.minAreaRect(points)
    points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

    index_a, index_b, index_c, index_d = 0, 1, 2, 3
    if points[1][1] > points[0][1]:
        index_a = 0
        index_d = 1
    else:
        index_a = 1
        index_d = 0
    if points[3][1] > points[2][1]:
        index_b = 2
        index_c = 3
    else:
        index_b = 3
        index_c = 2

    box = np.array(
        [points[index_a], points[index_b], points[index_c], points[index_d]]
    ).astype(np.int32)

    return box


def resize_img(img, input_size=600):
    """
    resize img and limit the longest side of the image to input_size
    """
    img = np.array(img)
    im_shape = img.shape
    im_size_max = np.max(im_shape[0:2])
    im_scale = float(input_size) / float(im_size_max)
    img = cv2.resize(img, None, None, fx=im_scale, fy=im_scale)
    return img


def det_router(width, height):
    if all([width < 800, height < 800]):
        return 640
    else:
        return 960


def rec_router(width, height):
    ratio = width / height

    if ratio <= 3:
        ratio_res = 3
    elif ratio <= 5:
        ratio_res = 5
    elif ratio <= 10:
        ratio_res = 10
    elif ratio <= 15:
        ratio_res = 15
    elif ratio <= 25:
        ratio_res = 25
    else:
        ratio_res = 35

    return ratio_res

def split_bbox_for_recognition(bbox, rec_image_shape, overlap_ratio=0.1):
    bbox = np.array(bbox, dtype=np.float32)

    width = max(np.linalg.norm(bbox[0] - bbox[1]), np.linalg.norm(bbox[2] - bbox[3]))
    height = max(np.linalg.norm(bbox[0] - bbox[3]), np.linalg.norm(bbox[1] - bbox[2]))
    rec_ratio = rec_image_shape[2] / rec_image_shape[1]  # W/H
    bbox_ratio = width / height
    
    if bbox_ratio > rec_ratio * 1.3:
        num_splits = math.ceil(bbox_ratio / rec_ratio)
        split_width = width / num_splits
        
        split_bboxes = []
        for i in range(num_splits):
            start_x = bbox[0][0] + (split_width * i)
            end_x = start_x + split_width + (split_width * overlap_ratio)
            
            split_bbox = np.array([
                [start_x, bbox[0][1]],  # top-left
                [end_x, bbox[1][1]],    # top-right
                [end_x, bbox[2][1]],    # bottom-right
                [start_x, bbox[3][1]]   # bottom-left
            ], dtype=np.float32)
            split_bboxes.append(split_bbox)
            
        return np.array(split_bboxes)
    else:
        return [bbox]


def merge_recognition_results(split_results, overlap_ratio=0.1):
    if not split_results:
        return "", 0.0
    
    texts = [r[0] for r in split_results]
    scores = [r[1] for r in split_results]
    overlap_chars = int(len(texts[0]) * overlap_ratio)
    merged_text = texts[0]
    for i in range(1, len(texts)):
        overlap_text1 = texts[i-1][-overlap_chars:]
        overlap_text2 = texts[i][:overlap_chars]
        
        if overlap_text1 == overlap_text2:
            merged_text += texts[i][overlap_chars:]
        else:
            score1 = scores[i-1]
            score2 = scores[i]
            if score1 >= score2:
                merged_text += texts[i][overlap_chars:]
            else:
                merged_text = merged_text[:-overlap_chars] + texts[i]
    
    merged_score = sum(scores) / len(scores)
    return merged_text, merged_score


def base64_to_cv2(b64str):
    import base64

    data = base64.b64decode(b64str.encode("utf8"))
    data = np.frombuffer(data, np.uint8)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return data


def str2bool(v):
    return v.lower() in ("true", "t", "1")


def filter_tag_det_res(dt_boxes, image_shape):
    img_height, img_width = image_shape[0], image_shape[1]
    dt_boxes_new = []
    for box in dt_boxes:
        if type(box) is list:
            box = np.array(box)
        box = order_points_clockwise(box)
        box = clip_det_res(box, img_height, img_width)
        rect_width = int(np.linalg.norm(box[0] - box[1]))
        rect_height = int(np.linalg.norm(box[0] - box[3]))
        if rect_width <= 3 or rect_height <= 3:
            continue
        dt_boxes_new.append(box)
    dt_boxes = np.array(dt_boxes_new)
    return dt_boxes


def order_points_clockwise(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    tmp = np.delete(pts, (np.argmin(s), np.argmax(s)), axis=0)
    diff = np.diff(np.array(tmp), axis=1)
    rect[1] = tmp[np.argmin(diff)]
    rect[3] = tmp[np.argmax(diff)]
    return rect


def clip_det_res(points, img_height, img_width):
    for pno in range(points.shape[0]):
        points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
        points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
    return points


def infer_args():
    parser = argparse.ArgumentParser()
    # params for prediction engine
    parser.add_argument("--use_gpu", type=str2bool, default=True)
    parser.add_argument("--use_xpu", type=str2bool, default=False)
    parser.add_argument("--use_npu", type=str2bool, default=False)
    parser.add_argument("--ir_optim", type=str2bool, default=True)
    parser.add_argument("--use_tensorrt", type=str2bool, default=False)
    parser.add_argument("--min_subgraph_size", type=int, default=15)
    parser.add_argument("--precision", type=str, default="fp32")
    parser.add_argument("--gpu_mem", type=int, default=500)
    parser.add_argument("--gpu_id", type=int, default=0)

    # params for text detector
    parser.add_argument("--image_dir", type=str)
    parser.add_argument("--page_num", type=int, default=0)
    parser.add_argument("--det_algorithm", type=str, default="DB")
    parser.add_argument(
        "--det_model_dir",
        type=str,
        default=str(module_dir / "models/onnx/det.onnx"),
    )
    parser.add_argument("--det_limit_side_len", type=float, default=960)
    parser.add_argument("--det_limit_type", type=str, default="max")
    parser.add_argument("--det_box_type", type=str, default="quad")

    # DB parmas
    parser.add_argument("--det_db_thresh", type=float, default=0.3)
    parser.add_argument("--det_db_box_thresh", type=float, default=0.6)
    parser.add_argument("--det_db_unclip_ratio", type=float, default=1.5)
    parser.add_argument("--max_batch_size", type=int, default=10)
    parser.add_argument("--use_dilation", type=str2bool, default=False)
    parser.add_argument("--det_db_score_mode", type=str, default="fast")

    # EAST parmas
    parser.add_argument("--det_east_score_thresh", type=float, default=0.8)
    parser.add_argument("--det_east_cover_thresh", type=float, default=0.1)
    parser.add_argument("--det_east_nms_thresh", type=float, default=0.2)

    # SAST parmas
    parser.add_argument("--det_sast_score_thresh", type=float, default=0.5)
    parser.add_argument("--det_sast_nms_thresh", type=float, default=0.2)

    # PSE parmas
    parser.add_argument("--det_pse_thresh", type=float, default=0)
    parser.add_argument("--det_pse_box_thresh", type=float, default=0.85)
    parser.add_argument("--det_pse_min_area", type=float, default=16)
    parser.add_argument("--det_pse_scale", type=int, default=1)

    # FCE parmas
    parser.add_argument("--scales", type=list, default=[8, 16, 32])
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--fourier_degree", type=int, default=5)

    # params for text recognizer
    parser.add_argument("--rec_algorithm", type=str, default="SVTR_LCNet")
    parser.add_argument(
        "--rec_model_dir",
        type=str,
        default=str(module_dir / "models/onnx/rec.onnx"),
    )
    parser.add_argument("--rec_image_inverse", type=str2bool, default=True)
    parser.add_argument("--rec_image_shape", type=str, default="3, 48, 320")
    parser.add_argument("--rec_batch_num", type=int, default=6)
    parser.add_argument("--max_text_length", type=int, default=25)
    parser.add_argument(
        "--rec_char_dict_path",
        type=str,
        default=str(module_dir / "models/ppocrv5_dict.txt"),
    )
    parser.add_argument("--use_space_char", type=str2bool, default=True)
    parser.add_argument(
        "--vis_font_path", type=str, default=str(module_dir / "fonts/simfang.ttf")
    )
    parser.add_argument("--drop_score", type=float, default=0.5)

    # params for e2e
    parser.add_argument("--e2e_algorithm", type=str, default="PGNet")
    parser.add_argument("--e2e_model_dir", type=str)
    parser.add_argument("--e2e_limit_side_len", type=float, default=768)
    parser.add_argument("--e2e_limit_type", type=str, default="max")

    # PGNet parmas
    parser.add_argument("--e2e_pgnet_score_thresh", type=float, default=0.5)
    parser.add_argument(
        "--e2e_char_dict_path",
        type=str,
        default=str(module_dir / "ppocr/utils/ic15_dict.txt"),
    )
    parser.add_argument("--e2e_pgnet_valid_set", type=str, default="totaltext")
    parser.add_argument("--e2e_pgnet_mode", type=str, default="fast")

    # params for text classifier
    parser.add_argument("--use_angle_cls", type=str2bool, default=False)
    parser.add_argument(
        "--cls_model_dir",
        type=str,
        default=str(module_dir / "models/onnx/cls.onnx"),
    )
    parser.add_argument("--cls_image_shape", type=str, default="3, 48, 192")
    parser.add_argument("--label_list", type=list, default=["0", "180"])
    parser.add_argument("--cls_batch_num", type=int, default=6)
    parser.add_argument("--cls_thresh", type=float, default=0.9)

    parser.add_argument("--enable_mkldnn", type=str2bool, default=False)
    parser.add_argument("--cpu_threads", type=int, default=10)
    parser.add_argument("--use_pdserving", type=str2bool, default=False)
    parser.add_argument("--warmup", type=str2bool, default=False)

    # SR parmas
    parser.add_argument("--sr_model_dir", type=str)
    parser.add_argument("--sr_image_shape", type=str, default="3, 32, 128")
    parser.add_argument("--sr_batch_num", type=int, default=1)

    #
    parser.add_argument(
        "--draw_img_save_dir", type=str, default=str(module_dir / "inference_results")
    )
    parser.add_argument("--save_crop_res", type=str2bool, default=False)
    parser.add_argument(
        "--crop_res_save_dir", type=str, default=str(module_dir / "output")
    )

    # multi-process
    parser.add_argument("--use_mp", type=str2bool, default=False)
    parser.add_argument("--total_process_num", type=int, default=1)
    parser.add_argument("--process_id", type=int, default=0)

    parser.add_argument("--benchmark", type=str2bool, default=False)
    parser.add_argument(
        "--save_log_path", type=str, default=str(module_dir / "log_output/")
    )

    parser.add_argument("--show_log", type=str2bool, default=True)
    parser.add_argument("--use_onnx", type=str2bool, default=False)
    return parser


def convert_boxes_to_quad_format(boxes):
    """
    Convert boxes from (n*4, 2) format to (n, 4, 2) format
    @param boxes: numpy array of shape (n*4, 2) or list of boxes where n is number of text boxes
    @return: numpy array of shape (n, 4, 2) where each box has 4 corner points
    """
    # Convert list to numpy array if needed
    if isinstance(boxes, list):
        if len(boxes) == 0:
            return np.array([])
        # Check if each element is already a box (4 points)
        if len(boxes[0]) == 4:
            # Already in correct format, just convert to numpy
            return np.array(boxes)
        else:
            # Flatten the list and convert to numpy
            boxes = np.array(boxes)
    
    if len(boxes.shape) == 2 and boxes.shape[1] == 2:
        # Check if the number of points is divisible by 4
        if boxes.shape[0] % 4 != 0:
            raise ValueError(f"Number of points ({boxes.shape[0]}) must be divisible by 4")
        
        # Reshape to (n, 4, 2) where n = boxes.shape[0] // 4
        num_boxes = boxes.shape[0] // 4
        boxes_reshaped = boxes.reshape(num_boxes, 4, 2)
        return boxes_reshaped
    elif len(boxes.shape) == 3 and boxes.shape[1] == 4 and boxes.shape[2] == 2:
        # Already in correct format
        return boxes
    else:
        raise ValueError(f"Unexpected box format: {boxes.shape}")


def sorted_boxes(dt_boxes: np.ndarray):
    """
    Sort text boxes from top-to-bottom, left-to-right order
    
    Args:
        dt_boxes: Detected text boxes
        
    Returns:
        List of sorted text boxes
    """
    _boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    for i in range(len(_boxes)-1):
        for j in range(i, -1, -1):
            if abs(_boxes[j + 1][0][1] - _boxes[j][0][1]) < 10 and (
                _boxes[j + 1][0][0] < _boxes[j][0][0]
            ):
                tmp = _boxes[j]
                _boxes[j] = _boxes[j + 1]
                _boxes[j + 1] = tmp
            else:
                break
    return _boxes


def rotate_if_vertical(crop):
    """
    Rotate crop if it's vertical (h > w*2)
    
    Args:
        crop: Cropped image
        
    Returns:
        Rotated crop if vertical, otherwise original crop
    """
    h, w = crop.shape[:2]
    if h > w * 2:
        return cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return crop
