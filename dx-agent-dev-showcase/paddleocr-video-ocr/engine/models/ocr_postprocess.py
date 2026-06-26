import numpy as np
import cv2
from shapely.geometry import Polygon
import pyclipper
import re


class DocOriPostProcess(object):
    def __init__(self, label_list=['0', '90', '180', '270'], **kwargs):
        super(DocOriPostProcess, self).__init__()
        self.label_list = label_list
        self.k = 1

    def __call__(self, preds):
        if preds.ndim == 2:
            preds = preds[0]
        logits = preds
        
        exp_values = np.exp(logits - np.max(logits))
        probabilities = exp_values / np.sum(exp_values)
        if max(probabilities) < 0.4:
            return [("0", 1.0)]
        
        topk_indices = np.argsort(probabilities)[::-1][:self.k]
        decode_out = [
            (self.label_list[idx], logits[idx]) for i, idx in enumerate(topk_indices)
        ]
        
        return decode_out


class ClsPostProcess(object):
    def __init__(self, label_list=['0', '180'], key=None, **kwargs):
        super(ClsPostProcess, self).__init__()
        self.label_list = label_list
        self.key = key

    def __call__(self, preds, label=None, *args, **kwargs):
        if self.key is not None:
            preds = preds[self.key]

        label_list = self.label_list
        if label_list is None:
            label_list = {idx: idx for idx in range(preds.shape[-1])}

        pred_idxs = preds.argmax(axis=1)

        decode_out = [
            (label_list[idx], preds[i, idx]) for i, idx in enumerate(pred_idxs)
        ]
        if label is None:
            return decode_out
        label = [(label_list[idx], 1.0) for idx in label]
        return decode_out, label

class DetPostProcess(object):

    """
    The post process for Differentiable Binarization (DB).
    """

    def __init__(
        self,
        thresh=0.3,
        box_thresh=0.7,
        max_candidates=1000,
        unclip_ratio=2.0,
        use_dilation=False,
        score_mode="fast",
        box_type="quad",
        **kwargs,
    ):
        self.thresh = thresh
        self.box_thresh = box_thresh
        self.max_candidates = max_candidates
        self.unclip_ratio = unclip_ratio
        self.min_size = 3
        self.score_mode = score_mode
        self.box_type = box_type
        assert score_mode in [
            "slow",
            "fast",
        ], "Score mode must be in [slow, fast] but got: {}".format(score_mode)

        self.dilation_kernel = None if not use_dilation else np.array([[1, 1], [1, 1]])
        
    def sort_boxes(self, boxes):
        """
        Sort boxes in reading order (top-to-bottom, left-to-right)
        
        Args:
            boxes: List of bbox coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            
        Returns:
            Sorted boxes with indices
        """
        # Calculate box centers for sorting
        box_centers = []
        for box in boxes:
            box_array = np.array(box)
            center_x = np.mean(box_array[:, 0])
            center_y = np.mean(box_array[:, 1])
            box_centers.append((center_x, center_y))
        
        # Sort by: 1) y-coordinate (top to bottom), 2) x-coordinate (left to right)
        sorted_indices = sorted(
            range(len(boxes)), 
            key=lambda i: (box_centers[i][1] // 10, box_centers[i][0])  # Group by rows
        )
        
        sorted_boxes = [boxes[i] for i in sorted_indices]
        return sorted_boxes, sorted_indices

    def polygons_from_bitmap(self, pred, _bitmap, dest_width, dest_height, padding_info=None):
        bitmap = _bitmap
        height, width = bitmap.shape

        boxes = []
        scores = []

        contours, _ = cv2.findContours(
            (bitmap * 255).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours[: self.max_candidates]:
            epsilon = 0.002 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = approx.reshape((-1, 2))
            if points.shape[0] < 4:
                continue

            score = self.box_score_fast(pred, points.reshape(-1, 2))
            if self.box_thresh > score:
                continue

            if points.shape[0] > 2:
                box = self.unclip(points, self.unclip_ratio)
                if len(box) > 1:
                    continue
            else:
                continue
            box = np.array(box).reshape(-1, 2)
            if len(box) == 0:
                continue

            _, sside = self.get_mini_boxes(box.reshape((-1, 1, 2)))
            if sside < self.min_size + 2:
                continue

            box = np.array(box)
            if padding_info is not None:
                orig_width = padding_info.get('orig_width', dest_width)
                orig_height = padding_info.get('orig_height', dest_height)
                padded_width = padding_info.get('padded_width', width)
                padded_height = padding_info.get('padded_height', height)
                
                # Scale from model output size to padded image size, then to original image size
                # Since padding is only applied to right/bottom (left=0, top=0), no offset needed
                scale_x = (padded_width / width) * (orig_width / padded_width)
                scale_y = (padded_height / height) * (orig_height / padded_height)
                
                # Simplified: scale_x = orig_width / width, scale_y = orig_height / height
                box[:, 0] = np.clip(box[:, 0] * orig_width / width, 0, orig_width)
                box[:, 1] = np.clip(box[:, 1] * orig_height / height, 0, orig_height)
            else:
                box[:, 0] = np.clip(np.round(box[:, 0] / width * dest_width), 0, dest_width)
                box[:, 1] = np.clip(np.round(box[:, 1] / height * dest_height), 0, dest_height)
                
            boxes.append(box.tolist())
            scores.append(score)
        return boxes, scores

    def boxes_from_bitmap(self, pred, _bitmap, dest_width, dest_height, padding_info=None):
        bitmap = _bitmap
        height, width = bitmap.shape

        outs = cv2.findContours(
            (bitmap * 255).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        if len(outs) == 3:
            img, contours, _ = outs[0], outs[1], outs[2]
        elif len(outs) == 2:
            contours, _ = outs[0], outs[1]

        num_contours = min(len(contours), self.max_candidates)

        boxes = []
        scores = []
        for index in range(num_contours):
            contour = contours[index]
            points, sside = self.get_mini_boxes(contour)
            if sside < self.min_size:
                continue
            points = np.array(points)
            if self.score_mode == "fast":
                score = self.box_score_fast(pred, points.reshape(-1, 2))
            else:
                score = self.box_score_slow(pred, contour)
            if self.box_thresh > score:
                continue

            box = self.unclip(points, self.unclip_ratio)
            if len(box) > 1:
                continue
            box = np.array(box).reshape(-1, 1, 2)
            box, sside = self.get_mini_boxes(box)
            if sside < self.min_size + 2:
                continue
            box = np.array(box)
            
            if padding_info is not None:
                pad_left = padding_info.get('left', 0)
                pad_top = padding_info.get('top', 0)
                orig_width = padding_info.get('orig_width', dest_width)
                orig_height = padding_info.get('orig_height', dest_height)
                padded_width = padding_info.get('padded_width', width)
                padded_height = padding_info.get('padded_height', height)
                
                # Step 1: Scale from model output size to padded image size
                scale_x = padded_width / width
                scale_y = padded_height / height
                box[:, 0] = box[:, 0] * scale_x
                box[:, 1] = box[:, 1] * scale_y
                
            else:
                box[:, 0] = np.clip(np.round(box[:, 0] / width * dest_width), 0, dest_width)
                box[:, 1] = np.clip(np.round(box[:, 1] / height * dest_height), 0, dest_height)
                
            boxes.append(box.astype("int32"))
            scores.append(score)
        return np.array(boxes, dtype="int32"), scores

    def unclip(self, box, unclip_ratio):
        poly = Polygon(box)
        distance = poly.area * unclip_ratio / poly.length
        offset = pyclipper.PyclipperOffset()
        offset.AddPath(box, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        expanded = offset.Execute(distance)
        return expanded

    def get_mini_boxes(self, contour):
        bounding_box = cv2.minAreaRect(contour)
        points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

        index_1, index_2, index_3, index_4 = 0, 1, 2, 3
        if points[1][1] > points[0][1]:
            index_1 = 0
            index_4 = 1
        else:
            index_1 = 1
            index_4 = 0
        if points[3][1] > points[2][1]:
            index_2 = 2
            index_3 = 3
        else:
            index_2 = 3
            index_3 = 2
        box = [points[index_1], points[index_2], points[index_3], points[index_4]]
        return box, min(bounding_box[1])

    def box_score_fast(self, bitmap, _box):
        """
        box_score_fast: use bbox mean score as the mean score
        """
        h, w = bitmap.shape[:2]
        box = _box.copy()
        xmin = np.clip(np.floor(box[:, 0].min()).astype("int32"), 0, w - 1)
        xmax = np.clip(np.ceil(box[:, 0].max()).astype("int32"), 0, w - 1)
        ymin = np.clip(np.floor(box[:, 1].min()).astype("int32"), 0, h - 1)
        ymax = np.clip(np.ceil(box[:, 1].max()).astype("int32"), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)
        box[:, 0] = box[:, 0] - xmin
        box[:, 1] = box[:, 1] - ymin
        cv2.fillPoly(mask, box.reshape(1, -1, 2).astype("int32"), 1)
        return cv2.mean(bitmap[ymin : ymax + 1, xmin : xmax + 1], mask)[0]

    def box_score_slow(self, bitmap, contour):
        """
        box_score_slow: use polyon mean score as the mean score
        """
        h, w = bitmap.shape[:2]
        contour = contour.copy()
        contour = np.reshape(contour, (-1, 2))

        xmin = np.clip(np.min(contour[:, 0]), 0, w - 1)
        xmax = np.clip(np.max(contour[:, 0]), 0, w - 1)
        ymin = np.clip(np.min(contour[:, 1]), 0, h - 1)
        ymax = np.clip(np.max(contour[:, 1]), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)

        contour[:, 0] = contour[:, 0] - xmin
        contour[:, 1] = contour[:, 1] - ymin

        cv2.fillPoly(mask, contour.reshape(1, -1, 2).astype("int32"), 1)
        return cv2.mean(bitmap[ymin : ymax + 1, xmin : xmax + 1], mask)[0]

    def __call__(self, outputs, origin_shape, padding_info=None):
        pred = outputs
        pred = np.array(pred)
        pred = pred[:, 0, :, :]
        segmentation = pred > self.thresh

        boxes_batch = []
        for batch_index in range(pred.shape[0]):
            src_h, src_w = origin_shape[0], origin_shape[1]
            if self.dilation_kernel is not None:
                mask = cv2.dilate(
                    np.array(segmentation[batch_index]).astype(np.uint8),
                    self.dilation_kernel,
                )
            else:
                mask = segmentation[batch_index]
            if self.box_type == "poly":
                boxes, scores = self.polygons_from_bitmap(
                    pred[batch_index], mask, src_w, src_h, padding_info
                )
            elif self.box_type == "quad":
                boxes, scores = self.boxes_from_bitmap(
                    pred[batch_index], mask, src_w, src_h, padding_info
                )
            else:
                raise ValueError("box_type can only be one of ['quad', 'poly']")
            
            if len(boxes) > 0:
                sorted_boxes, sorted_indices = self.sort_boxes(boxes)
                sorted_scores = [scores[i] for i in sorted_indices]
                boxes = sorted_boxes
                scores = sorted_scores
            
            boxes_batch.append({"points": boxes})
        return boxes_batch
    

class RecLabelDecode(object):
    """Convert between text-label and text-index"""

    def __init__(self, character_dict_path="ppocr_keys_v1.txt", use_space_char=True, **kwargs):
        self.beg_str = "sos"
        self.end_str = "eos"
        self.reverse = False
        self.character_str = []

        if character_dict_path is None:
            self.character_str = "0123456789abcdefghijklmnopqrstuvwxyz"
            dict_character = list(self.character_str)
        else:
            with open(character_dict_path, "rb") as fin:
                lines = fin.readlines()
                for line in lines:
                    line = line.decode("utf-8").strip("\n").strip("\r\n")
                    self.character_str.append(line)
            if use_space_char:
                self.character_str.append(" ")
            dict_character = list(self.character_str)
            if "arabic" in character_dict_path:
                self.reverse = True

        dict_character = self.add_special_char(dict_character)
        self.dict = {}
        for i, char in enumerate(dict_character):
            self.dict[char] = i
        self.character = dict_character

    def pred_reverse(self, pred):
        pred_re = []
        c_current = ""
        for c in pred:
            if not bool(re.search("[a-zA-Z0-9 :*./%+-]", c)):
                if c_current != "":
                    pred_re.append(c_current)
                pred_re.append(c)
                c_current = ""
            else:
                c_current += c
        if c_current != "":
            pred_re.append(c_current)

        return "".join(pred_re[::-1])

    def add_special_char(self, dict_character):
        return dict_character

    def get_word_info(self, text, selection):
        state = None
        word_content = []
        word_col_content = []
        word_list = []
        word_col_list = []
        state_list = []
        valid_col = np.where(selection == True)[0]

        for c_i, char in enumerate(text):
            if "\u4e00" <= char <= "\u9fff":
                c_state = "cn"
            elif bool(re.search("[a-zA-Z0-9]", char)):
                c_state = "en&num"
            else:
                c_state = "splitter"

            if (
                char == "."
                and state == "en&num"
                and c_i + 1 < len(text)
                and bool(re.search("[0-9]", text[c_i + 1]))
            ):
                c_state = "en&num"
            if (
                char == "-" and state == "en&num"
            ):
                c_state = "en&num"

            if state == None:
                state = c_state

            if state != c_state:
                if len(word_content) != 0:
                    word_list.append(word_content)
                    word_col_list.append(word_col_content)
                    state_list.append(state)
                    word_content = []
                    word_col_content = []
                state = c_state

            if state != "splitter":
                word_content.append(char)
                word_col_content.append(valid_col[c_i])

        if len(word_content) != 0:
            word_list.append(word_content)
            word_col_list.append(word_col_content)
            state_list.append(state)

        return word_list, word_col_list, state_list

    def decode(
        self,
        text_index,
        text_prob=None,
        is_remove_duplicate=False,
        return_word_box=False,
    ):
        """convert text-index into text-label."""
        result_list = []
        ignored_tokens = self.get_ignored_tokens()
        batch_size = len(text_index)
        for batch_idx in range(batch_size):
            selection = np.ones(len(text_index[batch_idx]), dtype=bool)
            if is_remove_duplicate:
                selection[1:] = text_index[batch_idx][1:] != text_index[batch_idx][:-1]
            for ignored_token in ignored_tokens:
                selection &= text_index[batch_idx] != ignored_token

            char_list = [
                self.character[text_id] for text_id in text_index[batch_idx][selection]
            ]
            if text_prob is not None:
                conf_list = text_prob[batch_idx][selection]
            else:
                conf_list = [1] * len(selection)
            if len(conf_list) == 0:
                conf_list = [0]

            text = "".join(char_list)

            if self.reverse:  # for arabic rec
                text = self.pred_reverse(text)

            if return_word_box:
                word_list, word_col_list, state_list = self.get_word_info(
                    text, selection
                )
                result_list.append(
                    (
                        text,
                        np.mean(conf_list).tolist(),
                        [
                            len(text_index[batch_idx]),
                            word_list,
                            word_col_list,
                            state_list,
                        ],
                    )
                )
            else:
                result_list.append((text, np.mean(conf_list).tolist()))
        return result_list

    def get_ignored_tokens(self):
        return [0]  # for ctc blank

    def __call__(self, preds, label=None, return_word_box=False, *args, **kwargs):
        if isinstance(preds, tuple) or isinstance(preds, list):
            preds = preds[-1]
        preds_idx = preds.argmax(axis=2)
        preds_prob = preds.max(axis=2)
        text = self.decode(
            preds_idx,
            preds_prob,
            is_remove_duplicate=True,
            return_word_box=return_word_box,
        )
        if return_word_box:
            for rec_idx, rec in enumerate(text):
                wh_ratio = kwargs["wh_ratio_list"][rec_idx]
                max_wh_ratio = kwargs["max_wh_ratio"]
                rec[2][0] = rec[2][0] * (wh_ratio / max_wh_ratio)
        if label is None:
            return text
        label = self.decode(label)
        return text, label

    def add_special_char(self, dict_character):
        dict_character = ["blank"] + dict_character
        return dict_character