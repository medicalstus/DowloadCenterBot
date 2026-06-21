# coding=utf-8
"""
HTTP data layer for the bot.

Replaces the old direct-MySQL `utils/sql.py`: every read/write now goes to the
medical_website backend over HTTPS, authenticated with the shared X-Bot-Key.
The bot keeps its own Telegram token in .env; no database lives here anymore.
"""

import requests

from utils.env import API_BASE_URL, API_KEY


_session = requests.Session()
_session.headers.update({"X-Bot-Key": API_KEY})
TIMEOUT = 20


def _url(path):
    return f"{API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def _get(path, params=None):
    r = _session.get(_url(path), params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path, json=None):
    r = _session.post(_url(path), json=json or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {}


def _patch(path, json=None):
    r = _session.patch(_url(path), json=json or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {}


def _put(path, json=None):
    r = _session.put(_url(path), json=json or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {}


def _delete(path):
    r = _session.delete(_url(path), timeout=TIMEOUT)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


# ── Users ─────────────────────────────────────────────────────────────────────

def user_get(id):
    try:
        return _get(f"tgbot/users/{id}")["data"]
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def user_ids():
    return [u["id"] for u in _get("tgbot/users", {"all": 1})["data"]]


def users_all():
    return _get("tgbot/users", {"all": 1})["data"]


def user_add(id, username, name, number):
    return _post("tgbot/users", {"id": id, "username": username or "", "name": name or "", "number": number or ""})["data"]


def user_update(id, username=None, name=None, number=None):
    payload = {}
    if username is not None:
        payload["username"] = username or ""
    if name is not None:
        payload["name"] = name or ""
    if number is not None:
        payload["number"] = number or ""
    return _patch(f"tgbot/users/{id}", payload).get("data")


# ── Admins ────────────────────────────────────────────────────────────────────

def admin_ids(types=None):
    """All admin telegram ids, optionally filtered to the given type(s)."""
    params = {}
    if types:
        params["type"] = ",".join(types) if isinstance(types, (list, tuple)) else types
    return [a["id"] for a in _get("tgbot/admins", params)["data"]]


def admins_list(type=None):
    params = {"type": type} if type else None
    return _get("tgbot/admins", params)["data"]


def admin_get(id):
    try:
        return _get(f"tgbot/admins/{id}")["data"]
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def admin_add(id, type="admin"):
    return _post("tgbot/admins", {"id": id, "type": type})["data"]


def admin_delete(id):
    return _delete(f"tgbot/admins/{id}")


# ── Categories ────────────────────────────────────────────────────────────────

def categories_roots():
    return _get("tgbot/categories", {"roots": 1})["data"]


def categories_by_top(top):
    return _get("tgbot/categories", {"top": top})["data"]


def category_add(name, top, step):
    return _post("tgbot/categories", {"name": name, "top": top, "step": step})["data"]


def category_delete(id, cascade=True):
    return _delete(f"tgbot/categories/{id}" + ("?cascade=1" if cascade else ""))


# ── Files ─────────────────────────────────────────────────────────────────────

def files_by_category(category):
    return _get("tgbot/files", {"category": category})["data"]


def file_get(id):
    try:
        return _get(f"tgbot/files/{id}")["data"]
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def file_add(category, name, step, file_id):
    return _post("tgbot/files", {"category": category, "name": name, "step": step, "file_id": file_id})["data"]


def file_update(id, **fields):
    return _patch(f"tgbot/files/{id}", fields).get("data")


def file_delete(id):
    return _delete(f"tgbot/files/{id}")


def file_increment(id):
    return _post(f"tgbot/files/{id}/increment")


# ── Download-center notes (the bot's جزوه‌ها come from the download center) ──

def dc_categories(parent=0):
    return _get("tgbot/dc-categories", {"parent": parent})["data"]


def dc_files(category=0):
    return _get("tgbot/dc-files", {"category": category})["data"]


def dc_file_increment(id):
    return _post(f"tgbot/dc-files/{id}/increment")


# ── Channels ──────────────────────────────────────────────────────────────────

def channels_list():
    return _get("tgbot/channels")["data"]


def channel_ids():
    return [c["channel"] for c in channels_list()]


def channel_add(channel, name):
    return _post("tgbot/channels", {"channel": channel, "name": name})["data"]


def channel_delete(id):
    return _delete(f"tgbot/channels/{id}")


# ── Messages (named forwarded-message albums) ────────────────────────────────

def message_get(name):
    return _get(f"tgbot/messages/{name}")["data"]["list"]


def message_set(name, lst):
    return _put(f"tgbot/messages/{name}", {"list": lst})["data"]


# ── Texts (editable copy: buttons + captions) ────────────────────────────────

_texts_cache = {}


def texts(refresh=False):
    global _texts_cache
    if refresh or not _texts_cache:
        _texts_cache = _get("tgbot/texts")["data"]
    return _texts_cache


def text(key, default=""):
    return texts().get(key, default) or default


def texts_set(mapping):
    global _texts_cache
    data = _put("tgbot/texts", mapping)["data"]
    _texts_cache = data
    return data


# ── Settings / stats ──────────────────────────────────────────────────────────

def set_username(username):
    return _patch("tgbot/settings", {"username": username})["data"]


def stats():
    return _get("tgbot/stats")["data"]
