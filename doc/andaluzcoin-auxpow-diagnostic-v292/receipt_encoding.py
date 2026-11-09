"""Canonical JSON and complete-frame encoding for the v0.2.92 review candidate."""

import hashlib
import json
import re


MAX_PAYLOAD = 4096
MAX_JOURNAL_PAYLOAD = 16383
MAX_CONTAINER_DEPTH = 8
MAX_MEMBERS = 48
MAX_ARRAY_ITEMS = 32
MAX_KEY_BYTES = 48
MAX_STRING_BYTES = 4096


def _quote(value):
    # Strict UTF-8 also rejects lone Unicode surrogates.
    if len(value) > MAX_STRING_BYTES or len(value.encode('utf-8')) > MAX_STRING_BYTES:
        raise ValueError('string exceeds bound')
    parts = ['"']
    for char in value:
        if ord(char) < 32:
            parts.append(f'\\u{ord(char):04x}')
        elif char in ('"', '\\'):
            parts.append('\\' + char)
        else:
            parts.append(char)
    parts.append('"')
    return ''.join(parts)


def _encode(value, depth, append):
    if type(value) is str:
        append(_quote(value))
        return
    if type(value) is bool:
        append('true' if value else 'false')
        return
    if type(value) not in (list, dict):
        raise ValueError('unsupported canonical value')
    if depth > MAX_CONTAINER_DEPTH:
        raise ValueError('container depth exceeds bound')
    if type(value) is list:
        if len(value) > MAX_ARRAY_ITEMS:
            raise ValueError('array exceeds item bound')
        append('[')
        for index, item in enumerate(value):
            if index:
                append(',')
            _encode(item, depth + 1, append)
        append(']')
        return
    if len(value) > MAX_MEMBERS:
        raise ValueError('object exceeds member bound')
    for key in value:
        if type(key) is not str or not key.isascii() or len(key) > MAX_KEY_BYTES:
            raise ValueError('invalid object key')
    append('{')
    for index, key in enumerate(sorted(value)):
        if index:
            append(',')
        append(_quote(key))
        append(':')
        _encode(value[key], depth + 1, append)
    append('}')


def _canonical_bytes(value, limit):
    if type(value) is not dict:
        raise ValueError('expected a top-level object')
    result = bytearray()

    def append(text):
        encoded = text.encode('utf-8')
        if len(encoded) > limit - len(result):
            raise ValueError('canonical payload exceeds bound')
        result.extend(encoded)

    _encode(value, 1, append)
    return bytes(result)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate object key')
        result[key] = value
    return result


def _reject_number(_):
    raise ValueError('JSON numeric tokens are forbidden')


def decode_payload(payload, *, journal=False):
    """Check encoding of an already bounded payload. Event fields need their own schema."""
    limit = MAX_JOURNAL_PAYLOAD if journal else MAX_PAYLOAD
    if type(payload) is not bytes or not 0 < len(payload) <= limit:
        raise ValueError('payload exceeds bounds')
    try:
        result = json.loads(payload.decode('utf-8'), object_pairs_hook=_unique_object,
                            parse_int=_reject_number, parse_float=_reject_number,
                            parse_constant=_reject_number)
    except RecursionError as exc:
        raise ValueError('container depth exceeds bound') from exc
    if _canonical_bytes(result, limit) != payload:
        raise ValueError('payload is not canonical')
    return result


def decode_frame(frame):
    """Read one complete pipe frame. The caller owns bounded I/O and partial reads."""
    if type(frame) is not bytes or not 4 < len(frame) <= 4 + MAX_PAYLOAD:
        raise ValueError('frame exceeds bounds')
    if int.from_bytes(frame[:4], 'little') != len(frame) - 4:
        raise ValueError('incorrect frame length')
    return decode_payload(frame[4:])


def encode_frame(payload):
    encoded = _canonical_bytes(payload, MAX_PAYLOAD)
    return len(encoded).to_bytes(4, 'little') + encoded


def event_digest(payload, previous_digest):
    """Hash the canonical two-member digest input specified by v0.2.91."""
    if type(payload) is not dict or type(previous_digest) is not str:
        raise ValueError('invalid digest input types')
    if not re.fullmatch('[0-9a-f]{64}', previous_digest):
        raise ValueError('invalid predecessor digest')
    encoded = _canonical_bytes({'payload': payload, 'previous_digest': previous_digest},
                               MAX_JOURNAL_PAYLOAD)
    return hashlib.sha256(encoded).hexdigest()
