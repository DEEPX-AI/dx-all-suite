import os
import random

import numpy as np
import cv2
import math
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from .utils import resize_img, get_minarea_rect

import time

module_dir = Path(__file__).resolve().parent
current_dir = os.path.dirname(os.path.abspath(__file__))

PIL_COLORS = ['lightgreen', 'pink', 'gold', 'lavender', 'sienna', 'turquoise', 'coral', 'gray']


def create_font(text, target_size, font_path=None):
    # Default Chinese font paths
    chinese_font_path = font_path


    if chinese_font_path and Path(chinese_font_path).exists():
        min_font_size = max(16, min(target_size) // 3)  # Much larger minimum
        max_font_size = min(150, max(target_size))  # Larger maximum
        
        best_font_size = min_font_size
        for font_size in range(min_font_size, max_font_size + 1, 2):  # Step by 2 for faster search
            font = ImageFont.truetype(chinese_font_path, font_size)
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if text_width <= (target_size[0] - 2) * 0.9 and text_height <= (target_size[1] - 2) * 0.9:
                best_font_size = font_size
            else:
                break
        
        final_font_size = min((best_font_size * 0.8), min_font_size)
        return ImageFont.truetype(chinese_font_path, final_font_size)
    elif chinese_font_path is None:
        return ImageFont.load_default()
    return ImageFont.load_default()

def create_font_vertical(text, target_size, font_path=None):
    chinese_font_path = font_path
    
    if chinese_font_path and Path(chinese_font_path).exists():
        char_height = target_size[1] // len(text) if len(text) > 0 else target_size[1]
        min_font_size = max(18, min(char_height // 2, target_size[0] // 2))
        max_font_size = min(150, min(char_height, target_size[0]))
        
        font_size = max(min_font_size, int(max_font_size * 0.8))
        return ImageFont.truetype(chinese_font_path, font_size)
    elif chinese_font_path is None:
        return ImageFont.load_default()

    return ImageFont.load_default()

def draw_vertical_text(draw, position, text, font, fill=(0, 0, 0), line_spacing=2):
    x, y = position
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        try:
            bbox = font.getbbox(char)
            char_height = bbox[3] - bbox[1]
        except:
            char_height = font.size
        y += char_height + line_spacing

def draw_box_txt_fine(img_size, box, txt, font_path=None):
    box = np.array(box, dtype=np.float32)
    box_height = int(
        math.sqrt((box[0][0] - box[3][0]) ** 2 + (box[0][1] - box[3][1]) ** 2)
    )
    box_width = int(
        math.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2)
    )

    padding = max(min(box_width, box_height) // 20, 2)  # Reduced padding: 5% or min 2px
    text_width = max(box_width - 3 * padding, 10)
    text_height = max(box_height - 3 * padding, 10)

    if box_height > 2 * box_width and box_height > 30:
        img_text = Image.new("RGB", (box_width, box_height), (255, 255, 255))
        draw_text = ImageDraw.Draw(img_text)
        if txt:
            font = create_font_vertical(txt, (text_width, text_height), font_path)
            start_x = (box_width - text_width) // 2
            start_y = padding
            draw_vertical_text(
                draw_text, (start_x, start_y), txt, font, fill=(0, 0, 0), line_spacing=2
            )
    else:
        img_text = Image.new("RGB", (box_width, box_height), (255, 255, 255))
        draw_text = ImageDraw.Draw(img_text)
        if txt:
            font = create_font(txt, (text_width, text_height), font_path)
            start_x = padding
            start_y = padding
            draw_text.text([start_x, start_y-2], txt, fill=(0, 0, 0), font=font)

    pts1 = np.float32(
        [[0, 0], [box_width, 0], [box_width, box_height], [0, box_height]]
    )
    
    pts2 = np.array(box, dtype=np.float32)
    M = cv2.getPerspectiveTransform(pts1, pts2)

    img_text = np.array(img_text, dtype=np.uint8)
    img_right_text = cv2.warpPerspective(
        img_text,
        M,
        img_size,
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )
    return img_right_text, (text_width, text_height)

def draw_box_txt_horizontal(img_size, box, txt, font_path=None):
    # NOTE: This function is useful when drawing directly on the original image.
    # Instead of returning img_size, it receives the original image img as a parameter.
    
    # 1. Calculate box size (retained)
    box = np.array(box, dtype=np.float32)
    # Find the min/max x, y from the 4-point coordinates to calculate the bounding box.
    # For horizontal text, the bounding box of the poly box determines the horizontal position of the text.
    x_coords = box[:, 0]
    y_coords = box[:, 1]
    
    left_top_x = x_coords[0]
    left_top_y = y_coords[0]
    min_x, max_x = int(np.min(x_coords)), int(np.max(x_coords))
    min_y, max_y = int(np.min(y_coords)), int(np.max(y_coords))
    
    box_width_bb = max_x - min_x
    box_height_bb = max_y - min_y
    
    # 2. Calculate text size and padding (retained)
    padding = max(min(box_width_bb, box_height_bb) // 20, 2)
    text_width = max(box_width_bb - 3 * padding, 10)
    text_height = max(box_height_bb - 3 * padding, 10)

    # 3. Generate horizontal text image (vertical text condition removed)
    # Only consider the space for horizontally placed text.
    
    font = create_font(txt, (text_width, text_height), font_path)
    
    # 4. Draw text directly on the original image
    # Create a white PIL image with img_size dimensions
    width, height = img_size
    img_pil = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img_pil)
    
    # Text starting coordinates: based on the top-left corner (min_x, min_y) of the poly box.
    # Apply padding to start slightly inward.
    start_x = left_top_x + padding
    start_y = left_top_y + padding
    
    # Draw text horizontally.
    draw.text([start_x, start_y - 2], txt, fill=(0, 0, 0), font=font)
    
    # Convert PIL image back to cv2 image and return
    img_result = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    return img_result

def transform_bbox_to_original(crop_bbox, original_poly, crop_image_shape=None):
    if isinstance(crop_bbox, list) and len(crop_bbox) == 8:
        crop_points = np.array([[crop_bbox[i], crop_bbox[i+1]] for i in range(0, 8, 2)], dtype=np.float32)
    elif isinstance(crop_bbox, list) and len(crop_bbox) == 4:
        x1, y1, x2, y2 = crop_bbox
        crop_points = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
    else:
        crop_points = np.array(crop_bbox, dtype=np.float32)
    
    original_poly = np.array(original_poly, dtype=np.float32)
    if len(original_poly.shape) == 1:
        original_poly = original_poly.reshape(-1, 2)
    
    x_min, y_min = np.min(original_poly, axis=0)
    x_max, y_max = np.max(original_poly, axis=0)
    orig_width = x_max - x_min
    orig_height = y_max - y_min
    
    if crop_image_shape is not None:
        crop_h, crop_w = crop_image_shape[:2]
        
        transformed_points = []
        for point in crop_points:
            if crop_w > 0 and crop_h > 0:
                scale_x = orig_width / crop_w
                scale_y = orig_height / crop_h
                
                orig_x = x_min + (point[0] * scale_x)
                orig_y = y_min + (point[1] * scale_y)
            else:
                orig_x, orig_y = x_min, y_min
                
            transformed_points.append([orig_x, orig_y])
    else:
        transformed_points = []
        for point in crop_points:
            if orig_width > 0 and orig_height > 0:
                norm_x = point[0] / orig_width if orig_width > 0 else 0
                norm_y = point[1] / orig_height if orig_height > 0 else 0
                
                orig_x = x_min + norm_x * orig_width
                orig_y = y_min + norm_y * orig_height
            else:
                orig_x, orig_y = x_min, y_min
                
            transformed_points.append([orig_x, orig_y])
    
    return np.array(transformed_points, dtype=np.float32)

def transform_bbox_to_original_precise(crop_bbox, original_poly, crop_image_shape):
    if isinstance(crop_bbox, list) and len(crop_bbox) == 8:
        crop_points = np.array([[crop_bbox[i], crop_bbox[i+1]] for i in range(0, 8, 2)], dtype=np.float32)
    elif isinstance(crop_bbox, list) and len(crop_bbox) == 4:
        x1, y1, x2, y2 = crop_bbox
        crop_points = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
    else:
        crop_points = np.array(crop_bbox, dtype=np.float32)
    
    original_poly = np.array(original_poly, dtype=np.float32)
    if len(original_poly.shape) == 1:
        original_poly = original_poly.reshape(-1, 2)
    
    crop_h, crop_w = crop_image_shape[:2]
    
    x_min, y_min = np.min(original_poly, axis=0)
    x_max, y_max = np.max(original_poly, axis=0)
    orig_width = x_max - x_min
    orig_height = y_max - y_min
    
    transformed_points = []
    for point in crop_points:
        if crop_w > 0 and crop_h > 0:
            scale_x = orig_width / crop_w
            scale_y = orig_height / crop_h
            
            orig_x = x_min + (point[0] * scale_x)
            orig_y = y_min + (point[1] * scale_y)
        else:
            orig_x, orig_y = x_min, y_min
            
        transformed_points.append([orig_x, orig_y])
    
    result = np.array(transformed_points, dtype=np.float32)
    
    return result

def transform_bbox_to_original_with_border(crop_bbox, original_poly, crop_image_shape, border_width=200):
    if isinstance(crop_bbox, list) and len(crop_bbox) == 8:
        crop_points = np.array([[crop_bbox[i], crop_bbox[i+1]] for i in range(0, 8, 2)], dtype=np.float32)
    elif isinstance(crop_bbox, list) and len(crop_bbox) == 4:
        x1, y1, x2, y2 = crop_bbox
        crop_points = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
    else:
        crop_points = np.array(crop_bbox, dtype=np.float32)
    
    original_poly = np.array(original_poly, dtype=np.float32)
    if len(original_poly.shape) == 1:
        original_poly = original_poly.reshape(-1, 2)
    
    crop_h, crop_w = crop_image_shape[:2]
    
    x_min, y_min = np.min(original_poly, axis=0)
    x_max, y_max = np.max(original_poly, axis=0)
    orig_width = x_max - x_min
    orig_height = y_max - y_min

    
    text_region_w = crop_w - 2 * border_width
    text_region_h = crop_h - 2 * border_width
    
    transformed_points = []
    for point in crop_points:
        text_x = point[0] - border_width
        text_y = point[1] - border_width
        
        if text_region_w > 0 and text_region_h > 0:
            scale_x = orig_width / text_region_w
            scale_y = orig_height / text_region_h
            
            orig_x = x_min + (text_x * scale_x)
            orig_y = y_min + (text_y * scale_y)
        else:
            orig_x, orig_y = x_min, y_min
            
        transformed_points.append([orig_x, orig_y])
    
    result = np.array(transformed_points, dtype=np.float32)
    
    return result

def save_to_img_custom_with_poly(image, bbox_text_poly_triplets, save_path, font_path=None):
    if isinstance(image, np.ndarray):
        img_pil = Image.fromarray(image.astype(np.uint8))
    else:
        img_pil = image
    
    w, h = img_pil.size
    
    img_left = img_pil.copy()
    img_right = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    random.seed(0)
    draw_left = ImageDraw.Draw(img_left)
    
    # Transform crop bboxes to original coordinates and create bbox_text_pairs
    bbox_text_pairs = []
    for crop_bbox, txt, original_poly in bbox_text_poly_triplets:
        try:
            # Transform crop bbox to original coordinates
            original_bbox = transform_bbox_to_original(crop_bbox, original_poly)
            bbox_text_pairs.append((original_bbox, txt))
        except Exception as e:
            continue
    
    # Use the existing visualization logic
    for bbox, txt in bbox_text_pairs:
        try:
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            
            if isinstance(bbox, list) and len(bbox) == 8:
                box = np.array([[bbox[i], bbox[i+1]] for i in range(0, 8, 2)])
            elif isinstance(bbox, list) and len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                box = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
            else:
                box = np.array(bbox)
            
            if len(box) > 4:
                pts = [(x, y) for x, y in box.tolist()]
                draw_left.polygon(pts, outline=color, width=8)
                box = get_minarea_rect(box)
                height = int(0.5 * (max(box[:, 1]) - min(box[:, 1])))
                box[:2, 1] = np.mean(box[:, 1])
                box[2:, 1] = np.mean(box[:, 1]) + min(20, height)
            
            box_pts = [(int(x), int(y)) for x, y in box.tolist()]
            draw_left.polygon(box_pts, fill=color)
            
            if txt.strip():
                img_right_text = draw_box_txt_fine((w, h), box, txt, font_path)
                pts = np.array(box, np.int32).reshape((-1, 1, 2))
                cv2.polylines(img_right_text, [pts], True, color, 1)
                img_right = cv2.bitwise_and(img_right, img_right_text)
        except Exception as e:
            continue
    
    img_left_array = np.array(img_left)
    img_original_array = np.array(img_pil)
    img_left_blended = Image.blend(
        Image.fromarray(img_original_array), 
        Image.fromarray(img_left_array), 
        0.5
    )
    
    img_show = Image.new("RGB", (w * 2, h), (255, 255, 255))
    img_show.paste(img_left_blended, (0, 0, w, h))
    img_show.paste(Image.fromarray(img_right), (w, 0, w * 2, h))
    
    save_path = Path(save_path)
    if not str(save_path).lower().endswith(('.jpg', '.png', '.jpeg')):
        save_path = save_path / "ocr_result.jpg"
    
    save_path.parent.mkdir(parents=True, exist_ok=True)
    img_show.save(save_path)
    
    return img_show

def poly2bbox(poly):
    L = poly[0]
    U = poly[1]
    R = poly[2]
    D = poly[5]
    L, R = min(L, R), max(L, R)
    U, D = min(U, D), max(U, D)
    bbox = [L, U, R, D]
    return bbox

def make_right_display_image(image, bboxes, texts, font_path=None, use_precise_transform=True):
    # If we only need the right display (white background with text), create it directly
    if font_path is None:
        font_path = os.path.join(module_dir, "fonts/NotoSansCJK-Regular.ttc")

    if isinstance(image, np.ndarray):
        img_pil = Image.fromarray(image.astype(np.uint8))
    else:
        img_pil = image

    w, h = img_pil.size
    img_right = np.ones((h, w, 3), dtype=np.uint8) * 255

    for i, poly_bbox in enumerate(bboxes):
        try:
            if texts[i].strip():
                pts = np.reshape(np.array(poly_bbox), [4, 2]).astype(np.int64)
                img_right_text = draw_box_txt_horizontal((w, h), pts.tolist(), texts[i], font_path)
                img_right = cv2.bitwise_and(img_right, img_right_text)
        except Exception as e:
            continue
    return Image.fromarray(img_right)

def make_left_display_image(image, bbox_text_poly_shape_quadruplets, use_precise_transform=True):
    
    if isinstance(image, np.ndarray):
        img_pil = Image.fromarray(image.astype(np.uint8))
    else:
        img_pil = image

    img_left = img_pil.copy()
    draw_left = ImageDraw.Draw(img_left)

    for poly_bbox in bbox_text_poly_shape_quadruplets:
        try:
            pts = np.reshape(np.array(poly_bbox), [4, 2]).astype(np.int64)
            draw_left.polygon(pts.tolist(), outline="green", width=3, fill='coral')
        except Exception as e:
            continue

    img_original_array = np.array(img_pil)
    img_left_array = np.array(img_left)
    img_left_blended = Image.blend(
        Image.fromarray(img_original_array), 
        Image.fromarray(img_left_array), 
        0.5
    )

    return img_left_blended

def draw_with_poly_enhanced(image, bbox_text_poly_shape_quadruplets, font_path=None, use_precise_transform=True):
    if font_path is None:
        font_path = os.path.join(module_dir, "fonts/NotoSansCJK-Regular.ttc")
    
    if isinstance(image, np.ndarray):
        image_rgb = image
        img_pil = Image.fromarray(image_rgb.astype(np.uint8))
    else:
        img_pil = image
    
    w, h = img_pil.size
    
    img_left = img_pil.copy()
    img_right = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    random.seed(0)
    draw_left = ImageDraw.Draw(img_left)
    
    for poly_bbox, txt, _, image_shape in bbox_text_poly_shape_quadruplets:
        try:
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            pts = np.reshape(np.array(poly_bbox), [4, 2]).astype(np.int64)
            draw_left.polygon(pts.tolist(), outline="green", width=3)
            
            if txt.strip():
                img_right_text, _ = draw_box_txt_fine((w, h), pts.tolist(), txt, font_path)
                img_right = cv2.bitwise_and(img_right, img_right_text)
        except Exception as e:
            continue
    
    img_left_array = np.array(img_left)
    img_original_array = np.array(img_pil)
    img_left_blended = Image.blend(
        Image.fromarray(img_original_array), 
        Image.fromarray(img_left_array), 
        0.5
    )
    
    # Add title space at the top
    title_height = 40
    total_height = h + title_height
    
    # Create new image with title space
    img_show = Image.new("RGB", (w * 2, total_height), (255, 255, 255))
    
    # Add titles
    draw_title = ImageDraw.Draw(img_show)
    title_font = ImageFont.truetype(font_path, 24) if font_path and Path(font_path).exists() else ImageFont.load_default()
    
    # Draw "Input Image" title on the left side
    left_title = "Input Image"
    left_bbox = title_font.getbbox(left_title)
    left_title_width = left_bbox[2] - left_bbox[0]
    left_title_x = (w - left_title_width) // 2
    draw_title.text((left_title_x, 10), left_title, fill=(0, 0, 0), font=title_font)
    
    # Draw "Result Text" title on the right side
    right_title = "Result Text"
    right_bbox = title_font.getbbox(right_title)
    right_title_width = right_bbox[2] - right_bbox[0]
    right_title_x = w + (w - right_title_width) // 2
    draw_title.text((right_title_x, 10), right_title, fill=(0, 0, 0), font=title_font)
    
    # Paste images below titles
    img_show.paste(img_left_blended, (0, title_height, w, total_height))
    img_show.paste(Image.fromarray(img_right), (w, title_height, w * 2, total_height))
    
    return img_show

def str_count(s):
    """
    Count the number of Chinese characters,
    a single English character and a single number
    equal to half the length of Chinese characters.
    args:
        s(string): the input of string
    return(int):
        the number of Chinese characters
    """
    import string

    count_zh = count_pu = 0
    s_len = len(str(s))
    en_dg_count = 0
    for c in str(s):
        if c in string.ascii_letters or c.isdigit() or c.isspace():
            en_dg_count += 1
        elif c.isalpha():
            count_zh += 1
        else:
            count_pu += 1
    return s_len - math.ceil(en_dg_count / 2)


def text_visual(
    texts,
    scores,
    img_h=400,
    img_w=600,
    threshold=0.0,
    font_path=str(module_dir / "fonts/simfang.ttf"),
):
    """
    create new blank img and draw txt on it
    args:
        texts(list): the text will be draw
        scores(list|None): corresponding score of each txt
        img_h(int): the height of blank img
        img_w(int): the width of blank img
        font_path: the path of font which is used to draw text
    return(array):
    """
    if scores is not None and texts is not None:
        assert len(texts) == len(scores), "The number of txts and corresponding scores must match"

    def create_blank_img():
        blank_img = np.ones(shape=[img_h, img_w], dtype=np.int8) * 255
        blank_img[:, img_w - 1 :] = 0
        blank_img = Image.fromarray(blank_img).convert("RGB")
        draw_txt = ImageDraw.Draw(blank_img)
        return blank_img, draw_txt

    blank_img, draw_txt = create_blank_img()

    font_size = 20
    font = ImageFont.truetype(font_path, font_size, encoding="utf-8")

    gap = font_size + 5
    txt_img_list = []
    count, index = 1, 0
    for idx, txt in enumerate(texts):
        index += 1
        if scores[idx] < threshold or math.isnan(scores[idx]):
            index -= 1
            continue
        
        # Handle empty or failed recognition text
        if not txt or txt.strip() == "":
            txt = "[NO_TEXT_DETECTED]"
            txt_color = (255, 0, 0)  # Red color for failed recognition
        else:
            txt_color = (0, 0, 0)  # Black color for successful recognition
            
        first_line = True
        while str_count(txt) >= img_w // font_size - 4:
            tmp = txt
            txt = tmp[: img_w // font_size - 4]
            if first_line:
                new_txt = str(index) + ": " + txt
                first_line = False
            else:
                new_txt = "    " + txt
            draw_txt.text((0, gap * count), new_txt, txt_color, font=font)
            txt = tmp[img_w // font_size - 4 :]
            if count >= img_h // gap - 1:
                txt_img_list.append(np.array(blank_img))
                blank_img, draw_txt = create_blank_img()
                count = 0
            count += 1
        if first_line:
            new_txt = str(index) + ": " + txt + "   " + "%.3f" % (scores[idx])
        else:
            new_txt = "  " + txt + "  " + "%.3f" % (scores[idx])
        draw_txt.text((0, gap * count), new_txt, txt_color, font=font)
        # whether add new blank img or not
        if count >= img_h // gap - 1 and idx + 1 < len(texts):
            txt_img_list.append(np.array(blank_img))
            blank_img, draw_txt = create_blank_img()
            count = 0
        count += 1
    txt_img_list.append(np.array(blank_img))
    if len(txt_img_list) == 1:
        blank_img = np.array(txt_img_list[0])
    else:
        blank_img = np.concatenate(txt_img_list, axis=1)
    return np.array(blank_img)


def draw_ocr(
    image,
    boxes,
    txts=None,
    scores=None,
    drop_score=0.5,
    font_path=str(module_dir / "fonts/simfang.ttf"),
):
    """
    Visualize the results of OCR detection and recognition
    args:
        image(Image|array): RGB image
        boxes(list): boxes with shape(N, 4, 2)
        txts(list): the texts
        scores(list): txxs corresponding scores
        drop_score(float): only scores greater than drop_threshold will be visualized
        font_path: the path of font which is used to draw text
    return(array):
        the visualized img
    """
    if scores is None:
        scores = [1] * len(boxes)
    box_num = len(boxes)
    
    # Ensure image is in the correct format for OpenCV
    if isinstance(image, np.ndarray):
        image = image.astype(np.uint8)
    else:
        image = np.array(image, dtype=np.uint8)
    
    # Make sure the array is contiguous in memory
    if not image.flags.c_contiguous:
        image = np.ascontiguousarray(image)
        
    for i in range(box_num):
        if scores is not None and (scores[i] < drop_score or math.isnan(scores[i])):
            continue
        box = np.reshape(np.array(boxes[i]), [-1, 1, 2]).astype(np.int64)
        
        # Determine box color and thickness based on text recognition result
        if txts is None or i >= len(txts) or not txts[i] or txts[i].strip() == "":
            # Red color with thicker line for boxes without recognized text
            box_color = (0, 0, 255)  # BGR format: Red
            thickness = 3
        else:
            # Green color for boxes with recognized text
            box_color = (0, 255, 0)  # BGR format: Green
            thickness = 2
        image = cv2.polylines(image, [box], True, box_color, thickness)
    if txts is not None:
        img = np.array(resize_img(image, input_size=600))
        txt_img = text_visual(
            txts,
            scores,
            img_h=img.shape[0],
            img_w=600,
            threshold=drop_score,
            font_path=font_path,
        )
        img = np.concatenate([np.array(img), np.array(txt_img)], axis=1)
        return img
    return image
