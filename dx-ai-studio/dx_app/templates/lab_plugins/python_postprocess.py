"""DX App Lab custom postprocess plugin scaffold.

This scaffold is intentionally not executable until its implementation replaces
the exception below. The Lab keeps workflows using it blocked until validation
finds a complete supported plugin.
"""


def postprocess(outputs, context):
    raise NotImplementedError("Implement postprocess(outputs, context)")