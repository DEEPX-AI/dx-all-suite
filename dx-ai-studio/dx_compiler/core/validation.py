"""Pure functions that check user input at the boundary.

Validation is organised **by field name, not by type**: `validate_enhanced_scheme` is the same
function whichever endpoint the field arrives on. Writing each rule in one place is what keeps
endpoints from handling the same field differently.

This module knows nothing about HTTP. It returns the clean value or raises ValidationError;
server.py turns that into a 400 in one place.
"""
from __future__ import annotations


class ValidationError(ValueError):
    """User input rejected at the boundary. Callers turn it into a 400.

    It subclasses ValueError because some callers (`_list_dir`, `_mkdir`) already
    catch ValueError to return a 400, and both mean "the value the user sent is wrong".
    """


# opt_level is not something only the model can tell. The vendor docs fix it as an enum:
# dx-compiler/source/docs/02_06_Execution_of_DX-COM.md:76
#   | `--opt_level` | `{0,1}` (Default: `1`) |
_OPT_LEVELS = (0, 1)


def validate_opt_level(raw) -> int:
    """Multipart fields arrive as strings: convert to int and check the range.

    `'abc'` and `''` must give a 400, not a ValueError (500). An empty form field really
    does send `''`.
    """
    if raw is None:
        return 1
    if isinstance(raw, bool):
        # In Python True is an instance of int, so filter it out first.
        raise ValidationError(f"Invalid opt_level: {raw!r} — must be one of {list(_OPT_LEVELS)}")
    if isinstance(raw, int):
        value = raw
    else:
        text = str(raw).strip()
        if not text:
            raise ValidationError(
                "Invalid opt_level: empty — must be one of " + str(list(_OPT_LEVELS)))
        try:
            value = int(text)
        except (TypeError, ValueError):
            raise ValidationError(
                f"Invalid opt_level: {raw!r} — must be one of {list(_OPT_LEVELS)}") from None
    if value not in _OPT_LEVELS:
        raise ValidationError(
            f"Invalid opt_level: {value} — must be one of {list(_OPT_LEVELS)}")
    return value


def validate_fs_path(raw, field: str, *, required: bool = True) -> str:
    """Check that a path field is a string.

    Where the path **points** is not checked here; `path_policy` does that (real files and
    folders inside the allowed roots). Models on external storage such as
    `/media/usb/model.onnx` work because /media and /mnt are allowed roots.

    Only the type is checked here: a non-string would make `.strip()` raise AttributeError (500).
    """
    if raw is None or raw == "":
        if required:
            raise ValidationError(f"{field} is required")
        return ""
    if not isinstance(raw, str):
        raise ValidationError(
            f"Invalid {field}: expected a path string, got {type(raw).__name__}")
    text = raw.strip()
    if not text and required:
        raise ValidationError(f"{field} is required")
    return text


def validate_node_names(raw, field: str) -> list:
    """A list of graph node names. **Strings are rejected.**

    The reason is subtle. A Python string is iterable, so ``set("ab")`` is ``{'a','b'}``.
    In a graph with one-letter node names those letters look like real nodes, and the server
    would answer **200 and select two nodes the user never named**, with no error at all:

        input_nodes="ab"    -> 200, read as nodes a and b   (wrong shape succeeds)
        input_nodes=["ab"]  -> 500, "ab not found"           (right shape fails)

    So no convenience here. Wrapping a lone string as ``[raw]`` looks friendly, but then the
    server has to guess whether "ab" is one node or two. Reject instead of guessing.
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        raise ValidationError(
            f"Invalid {field}: expected a list of node names, got a string. "
            f"A single node must still be a list — use [{raw!r}], not {raw!r}.")
    if not isinstance(raw, (list, tuple)):
        raise ValidationError(
            f"Invalid {field}: expected a list of node names, got {type(raw).__name__}")
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(
                f"Invalid {field}: {item!r} — node names must be non-empty strings")
    return list(raw)


def validate_enhanced_scheme_json(raw, field: str = "enhanced_scheme"):
    """Check only that the multipart enhanced_scheme **parses as JSON**.

    A parse failure must not silently become ``None``: the user asked for DXQ and would get a
    plain compile without a word. A silent wrong answer is worse than an error.

    Keys and values are checked by `validate_enhanced_scheme`, not here.
    """
    import json as _json

    if raw is None or raw == "":
        return None
    if not isinstance(raw, str):
        return raw
    try:
        return _json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"Invalid {field}: not valid JSON — {exc}") from None


# The names are similar but these are **not the same thing**. Do not merge them.
#
#   calibration_method in config.json   : {ema, minmax}
#       config-schema.md:76 lists only these two.
#   recalibration_method for resume     : {minmax, ema, iqr}
#       02_06_Execution_of_DX-COM.md:103 marks it "(Resume-only)".
#
# Merging them would let iqr into config.json.
_CALIBRATION_METHODS = ("ema", "minmax")
_RECALIBRATION_METHODS = ("ema", "iqr", "minmax")


def validate_calibration_method(raw):
    """calibration_method in config.json: only `{ema, minmax}`."""
    if raw is None or raw == "":
        return None
    # No separate type check: a non-string fails the membership test below anyway,
    # and that message shows both the value and the allowed set.
    if raw not in _CALIBRATION_METHODS:
        raise ValidationError(
            f"Invalid calibration_method: {raw!r} — "
            f"must be one of {list(_CALIBRATION_METHODS)}")
    return raw


def validate_recalibration_method(raw):
    """Resume only: `{minmax, ema, iqr}`.

    An empty string means "not set".
    """
    if raw is None:
        return None
    if isinstance(raw, str) and not raw.strip():
        return None
    if raw not in _RECALIBRATION_METHODS:   # no type branch, same reason as above
        raise ValidationError(
            f"recalibration_method must be one of {sorted(_RECALIBRATION_METHODS)}")
    return raw


# 02_06_Execution_of_DX-COM.md:490 — "Supported Schemes: DXQ-P0 through DXQ-P5"
_DXQ_KEYS = ("DXQ-P0", "DXQ-P1", "DXQ-P2", "DXQ-P3", "DXQ-P4", "DXQ-P5")


def validate_enhanced_scheme(raw):
    """A set of DXQ schemes. Keys are whitelisted; values must be objects.

    **Parameter names are not restricted.** They differ per scheme (02_06:493):
    `alpha`, `beta`, `cosim_num`, `num_samples`. Whitelisting them would over-block the way
    a transform-name whitelist would, and the documented list may not be current. Only
    check that each value is an object.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return _bad_scheme("enhanced_scheme must be a JSON object")
    bad = [k for k in raw if k not in _DXQ_KEYS]
    if bad:
        return _bad_scheme(f"Unknown DXQ key(s): {bad}. Valid: {sorted(_DXQ_KEYS)}")
    for key, params in raw.items():
        if not isinstance(params, dict):
            return _bad_scheme(
                f"Invalid enhanced_scheme[{key!r}]: expected an object of scheme "
                f"parameters, got {type(params).__name__}")
    return raw


def _bad_scheme(message: str):
    raise ValidationError(message)


# Only positive values can be a size. The rule is keyed on the parameter **name**:
# keyed on the transform name it would miss centercrop and need updating for every
# new transform.
_POSITIVE_PARAMS = ("width", "height", "size", "scale")

# Anything not listed is deliberately unchecked. Real configs in the repo use the same
# parameter both as a scalar and as a list:
#     {"transpose": {"axis": [2, 0, 1]}}   {"expandDim": {"axis": 0}}
#     {"div": {"x": 255.0}}                {"div": {"x": [255, 255, 255]}}
#     {"resize": {"pad_value": [114, 114, 114]}}   the UI default is the scalar 0
# Signs are free too (axis may be negative, as in numpy). A rule here would block configs
# that work today, so only parameters with a clear meaning are checked.


def _is_number(v) -> bool:
    """bool does not count as a number; in Python True is an instance of int."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_preprocessings(raw):
    """default_loader.preprocessings in config.json.

    The GUI parameter fields are free text and the collecting code does
    `isNaN(num) ? raw : num`, so whatever is typed is sent as is.

    **Transform names are not restricted.** The vendor registry (02_06:394) has resize2,
    resize3 and resize_tv, which the UI does not offer. Blocking by the UI list would reject
    valid configs, and the documented list may not be current. The compile step, which reads
    the model, judges the names.
    """
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ValidationError(
            "Invalid preprocessings: expected an array of operations, "
            f"got {type(raw).__name__}")
    for index, entry in enumerate(raw):
        _validate_one(entry, index)
    return raw


def _validate_one(entry, index: int) -> None:
    where = f"preprocessings[{index}]"
    if not isinstance(entry, dict):
        raise ValidationError(
            f"Invalid {where}: expected an object like "
            f'{{"resize": {{...}}}}, got {type(entry).__name__}')
    if len(entry) != 1:
        # With two transforms in one entry their order is unknown, and
        # preprocessings is an array **whose order matters**.
        raise ValidationError(
            f"Invalid {where}: expected exactly one transform per entry, "
            f"got {len(entry)} ({sorted(entry)}). Split them into separate entries.")

    name, params = next(iter(entry.items()))
    if params is None:
        return  # a transform without parameters, such as pil_2_cv
    if not isinstance(params, dict):
        raise ValidationError(
            f"Invalid {where}.{name}: expected an object of parameters, "
            f"got {type(params).__name__}")

    for key in _POSITIVE_PARAMS:
        if key in params:
            value = params[key]
            if not _is_number(value) or value <= 0:
                raise ValidationError(
                    f"Invalid {where}.{name}.{key}: {value!r} — must be a positive number")

    _validate_normalization(params, f"{where}.{name}")


def _validate_normalization(params: dict, where: str) -> None:
    """mean/std are per-channel values.

    Keyed on the **parameter name**, not the transform name: checking only normalize
    would miss variants such as normalize2. std is a divisor whatever the transform
    is called.
    """
    present = [k for k in ("mean", "std") if k in params]
    for key in present:
        value = params[key]
        if not isinstance(value, (list, tuple)) or not value:
            raise ValidationError(
                f"Invalid {where}.{key}: expected a non-empty list of per-channel "
                f"numbers, got {value!r}")
        for item in value:
            if not _is_number(item):
                raise ValidationError(
                    f"Invalid {where}.{key}: {item!r} — channel values must be numbers")
    if "std" in params:
        for item in params["std"]:
            if item == 0:
                raise ValidationError(
                    f"Invalid {where}.std: contains 0 — normalization divides by std")
    if len(present) == 2 and len(params["mean"]) != len(params["std"]):
        raise ValidationError(
            f"Invalid {where}: mean has {len(params['mean'])} channel(s) but std has "
            f"{len(params['std'])} — they must describe the same channels")


def validate_file_extensions(raw):
    """default_loader.file_extensions: an array of extensions.

    config-schema.md:126 shows it as an array: `["jpeg", "png", "jpg", "bmp"]`.
    Given the string `"jpg"`, dx_com iterates it per character and takes 'j', 'p', 'g'
    as extensions (the same trap as input_nodes in calculate-exclude).
    """
    if raw is None or raw == []:
        return None
    if isinstance(raw, str):
        raise ValidationError(
            f"Invalid file_extensions: expected a list, got a string. "
            f"Use [{raw!r}], not {raw!r}.")
    if not isinstance(raw, (list, tuple)):
        raise ValidationError(
            f"Invalid file_extensions: expected a list, got {type(raw).__name__}")
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(
                f"Invalid file_extensions: {item!r} — extensions must be non-empty strings")
    return list(raw)
