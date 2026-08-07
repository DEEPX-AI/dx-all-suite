"""DX-APP Asset access — files, images, videos, outputs."""

import os, hashlib
from pathlib import Path
from dx_app.core.config import DX_APP_ROOT, SAMPLE_DIR, OUTPUTS_DIR, ASSETS_DIR

_THUMB_CACHE_DIR = OUTPUTS_DIR.parent / ".thumb_cache"
_THUMB_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sample_thumbnail(rel, width=160):
    """Return a cached, downscaled JPEG thumbnail Path for an image asset under DX_APP_ROOT,
    or None if the source isn't a valid in-tree image.

    The composer asset grid renders 82x54px previews; without this it downloaded+decoded the
    full-resolution originals (90-480KB each). Cache key = source path + mtime + width, so an
    edited/replaced source regenerates. Path-traversal safe (must resolve under DX_APP_ROOT)."""
    try:
        src = (DX_APP_ROOT / rel).resolve()
        src.relative_to(DX_APP_ROOT.resolve())
    except (ValueError, OSError):
        return None
    if not src.is_file() or src.suffix.lower() not in _THUMB_EXT:
        return None
    try:
        mtime_ns = src.stat().st_mtime_ns
    except OSError:
        return None
    key = hashlib.sha1(f"{src}|{mtime_ns}|{width}".encode("utf-8")).hexdigest()
    out = _THUMB_CACHE_DIR / (key + ".jpg")
    if out.is_file():
        return out
    try:
        import cv2
        img = cv2.imread(str(src))
        if img is None:
            return None
        h, w = img.shape[:2]
        if w > width:
            nh = max(1, int(round(h * width / w)))
            img = cv2.resize(img, (width, nh), interpolation=cv2.INTER_AREA)
        # imencode (not imwrite): pick the JPEG encoder explicitly so the temp filename's
        # extension is irrelevant — imwrite chooses its writer by file extension and fails
        # on a ".tmp" name.
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if not ok:
            return None
        _THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # atomic publish so a concurrent reader never sees a half-written file
        tmp = out.with_name(out.name + f".{os.getpid()}.tmp")
        tmp.write_bytes(buf.tobytes())
        try:
            os.replace(str(tmp), str(out))
        except Exception:
            tmp.unlink(missing_ok=True)
            return None
        return out
    except Exception:
        return None


def get_file_content(rel):
    try:
        p=(DX_APP_ROOT/rel).resolve()
        if not str(p).startswith(str(DX_APP_ROOT.resolve())):return None
        if p.suffix not in{".hpp",".cpp",".py",".h",".json",".md"}:return None
        return p.read_text(errors="replace")
    except Exception:return None

def _scan_sample_img():
    d=SAMPLE_DIR/"img"
    if not d.is_dir():return[]
    _img_ext={".jpg",".jpeg",".png",".bmp"}
    out=[]
    for entry in sorted(d.iterdir()):
        if entry.is_file() and entry.suffix.lower() in _img_ext:
            out.append(str(entry.relative_to(DX_APP_ROOT)))
        elif entry.is_dir():
            has_img=any(
                f.is_file() and f.suffix.lower() in _img_ext
                for f in entry.iterdir()
            )
            if has_img:
                out.append(str(entry.relative_to(DX_APP_ROOT)))
    return out

def get_images(category=None):
    """List selectable run inputs.

    Without a category → the sample/img gallery (jpg/png/bmp), the historical
    behaviour. With a category whose default input lives OUTSIDE sample/img
    (3d_object_detection → LiDAR .bin, object_pose_estimation → DOPE png), scan
    that input's own directory for same-extension files instead — the sample/img
    jpgs are not valid inputs for those models and must not be offered.
    """
    if category:
        from dx_app.core.config import CAT_IMAGE
        default=CAT_IMAGE.get(category,"")
        if default and not default.startswith("sample/img/"):
            parent=(DX_APP_ROOT/default).parent
            ext=Path(default).suffix.lower()
            if parent.is_dir():
                out=[str(f.relative_to(DX_APP_ROOT))
                     for f in sorted(parent.iterdir())
                     if f.is_file() and f.suffix.lower()==ext]
                # Guarantee the default is present even if the dir scan missed it.
                if default not in out and (DX_APP_ROOT/default).is_file():
                    out.insert(0,default)
                return out
    return _scan_sample_img()

def get_videos(category=None):
    d=ASSETS_DIR/"videos"
    if not d.is_dir():return[]
    allv=[str(f.relative_to(DX_APP_ROOT)) for f in sorted(d.iterdir()) if f.suffix.lower() in{".mp4",".mov",".avi",".mkv"}]
    if category:
        from dx_app.core.config import CAT_VIDEO
        pref=CAT_VIDEO.get(category,"")
        if pref and pref in allv:
            return [pref]+[v for v in allv if v!=pref]
    return allv

def list_outputs():
    _IMG_EXT={".jpg",".jpeg",".png",".bmp",".webp"}
    _VID_EXT={".mp4",".mov",".avi",".mkv",".webm"}
    _ARC_EXT={".tar",".gz",".tgz",".zip",".tar.gz"}
    items=[]
    for f in OUTPUTS_DIR.iterdir():
        if not f.is_file():continue
        ext=f.suffix.lower()
        name=f.name
        if ext in _IMG_EXT:ftype="image"
        elif ext in _VID_EXT:ftype="video"
        elif any(name.endswith(a) for a in _ARC_EXT):ftype="archive"
        else:ftype="other"
        # Try to find matching source image for Before/After
        src_image=None
        if ftype=="image" and name.startswith("result_"):
            # result_yolov8n_123.jpg → try to find matching input in sample/
            import re
            m=re.match(r'result_([^_]+)_',name)
            if m:
                from dx_app.core.config import CAT_IMAGE
                model_hint=m.group(1)
                for cat,img in CAT_IMAGE.items():
                    if model_hint.lower() in cat.lower():
                        src_image=img;break
        items.append({"name":name,"size":f.stat().st_size,"mtime":f.stat().st_mtime,
                       "url":f"/outputs/{name}","type":ftype,"src_image":src_image})
    return sorted(items,key=lambda x:x["mtime"],reverse=True)

def delete_output(name):
    """Delete a single file from the outputs directory."""
    if not name or ".." in name or "/" in name:
        return {"error":"Invalid filename"}
    fp=OUTPUTS_DIR/name
    if not fp.is_file():
        return {"error":"File not found"}
    try:
        fp.unlink()
        return {"ok":True,"deleted":name}
    except Exception as e:
        return {"error":str(e)}
