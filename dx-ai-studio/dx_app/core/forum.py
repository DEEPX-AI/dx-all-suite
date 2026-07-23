"""DX-APP Forum — JSON-file backed community board.

Posts and comments are stored in forum_data.json next to this app.
No authentication: users choose a nickname; likes are tracked by
a browser-local token (UUID stored in localStorage).
"""
import json, time, uuid, threading
from pathlib import Path
from dx_app.core.config import SCRIPT_DIR

_FORUM_FILE = SCRIPT_DIR / "forum_data.json"
_lock = threading.Lock()
_VALID_CATS = {"ask_deepx", "community"}
_VALID_SORT = {"latest", "likes", "comments"}


def _load():
    if _FORUM_FILE.exists():
        try:
            return json.loads(_FORUM_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posts": []}


def _save(data):
    _FORUM_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )


def forum_list(sort="latest", category=None, q=None):
    """Return post list (summary view — no full body)."""
    with _lock:
        data = _load()
    posts = data["posts"][:]

    if category and category in _VALID_CATS:
        posts = [p for p in posts if p.get("category") == category]

    if q and q.strip():
        q_lo = q.lower()
        posts = [
            p for p in posts
            if q_lo in p.get("title", "").lower()
            or q_lo in p.get("body", "").lower()
        ]

    if sort == "likes":
        posts.sort(key=lambda p: len(p.get("likes", [])), reverse=True)
    elif sort == "comments":
        posts.sort(key=lambda p: len(p.get("comments", [])), reverse=True)
    else:  # latest
        posts.sort(key=lambda p: p.get("created_at", 0), reverse=True)

    result = []
    for p in posts:
        result.append({
            "id":            p["id"],
            "title":         p["title"],
            "body_preview":  p.get("body", "")[:150],
            "category":      p.get("category", "community"),
            "author":        p.get("author", "Anonymous"),
            "created_at":    p.get("created_at", 0),
            "likes":         len(p.get("likes", [])),
            "comment_count": len(p.get("comments", [])),
            "tags":          p.get("tags", []),
        })
    return {"posts": result, "total": len(result)}


def forum_get(post_id):
    """Return full post including all comments."""
    with _lock:
        data = _load()
    for p in data["posts"]:
        if p["id"] == post_id:
            return p
    return None


def forum_create(title, body, category="community", author="Anonymous", tags=None):
    """Create a new post. Returns the created post dict (or error dict)."""
    title = (title or "").strip()
    if not title:
        return {"error": "title required"}
    if len(title) > 100:
        return {"error": "title too long (max 100 characters)"}
    category = category if category in _VALID_CATS else "community"
    with _lock:
        data = _load()
        post = {
            "id":         uuid.uuid4().hex[:8],
            "title":      title,
            "body":       (body or "").strip(),
            "category":   category,
            "author":     ((author or "").strip() or "Anonymous")[:30],
            "tags":       [t.strip() for t in (tags or []) if t.strip()][:5],
            "created_at": time.time(),
            "likes":      [],
            "comments":   [],
        }
        data["posts"].insert(0, post)
        _save(data)
    return post


def forum_like(post_id, user_token):
    """Toggle like on a post. Returns {likes, liked}."""
    if not user_token:
        return {"error": "user_token required"}
    with _lock:
        data = _load()
        for p in data["posts"]:
            if p["id"] == post_id:
                likes = p.setdefault("likes", [])
                if user_token in likes:
                    likes.remove(user_token)
                    liked = False
                else:
                    likes.append(user_token)
                    liked = True
                _save(data)
                return {"likes": len(likes), "liked": liked}
    return {"error": "post not found"}


def forum_comment(post_id, body, author="Anonymous"):
    """Add a comment. Returns the new comment dict (or error)."""
    body = (body or "").strip()
    if not body:
        return {"error": "body required"}
    with _lock:
        data = _load()
        for p in data["posts"]:
            if p["id"] == post_id:
                comment = {
                    "id":         uuid.uuid4().hex[:8],
                    "body":       body,
                    "author":     ((author or "").strip() or "Anonymous")[:30],
                    "created_at": time.time(),
                    "likes":      [],
                }
                p.setdefault("comments", []).append(comment)
                _save(data)
                return comment
    return {"error": "post not found"}


def forum_comment_like(post_id, comment_id, user_token):
    """Toggle like on a comment. Returns {likes, liked}."""
    if not user_token:
        return {"error": "user_token required"}
    with _lock:
        data = _load()
        for p in data["posts"]:
            if p["id"] == post_id:
                for c in p.get("comments", []):
                    if c["id"] == comment_id:
                        likes = c.setdefault("likes", [])
                        if user_token in likes:
                            likes.remove(user_token)
                            liked = False
                        else:
                            likes.append(user_token)
                            liked = True
                        _save(data)
                        return {"likes": len(likes), "liked": liked}
    return {"error": "not found"}


def forum_delete(post_id, author):
    """Delete a post — only allowed for the original author."""
    with _lock:
        data = _load()
        for i, p in enumerate(data["posts"]):
            if p["id"] == post_id and p.get("author") == author:
                data["posts"].pop(i)
                _save(data)
                return {"ok": True}
    return {"error": "not found or unauthorized"}
