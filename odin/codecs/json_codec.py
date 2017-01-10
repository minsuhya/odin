# -*- coding: utf-8 -*-
import datetime

from odin import bases
from odin import serializers, resources, ResourceAdapter
from odin.exceptions import CodecDecodeError, CodecEncodeError

try:
    import simplejson as json
except ImportError:
    import json

JSON_TYPES = {
    datetime.date: serializers.date_iso_format,
    datetime.time: serializers.time_iso_format,
    datetime.datetime: serializers.datetime_iso_format,
}
CONTENT_TYPE = 'application/json'


class OdinEncoder(json.JSONEncoder):
    """
    Encoder for Odin resources.
    """
    def __init__(self, include_virtual_fields=True, include_type_field=True, *args, **kwargs):
        super(OdinEncoder, self).__init__(*args, **kwargs)
        self.include_virtual_fields = include_virtual_fields
        self.include_type_field = include_type_field

    def default(self, o):
        if isinstance(o, (resources.ResourceBase, ResourceAdapter)):
            obj = o.to_dict(self.include_virtual_fields)
            if self.include_type_field:
                obj[o._meta.type_field] = o._meta.resource_name
            return obj
        elif isinstance(o, bases.ResourceIterable):
            return list(o)
        elif o.__class__ in JSON_TYPES:
            return JSON_TYPES[o.__class__](o)
        return super(OdinEncoder, self)


class JsonCodec(bases.DocumentCodec):
    MIME_TYPE = 'application/json'

    def __init__(self, encoder_cls=OdinEncoder, default_to_not_supplied=False, **kwargs):
        """
        :param encoder_cls: Encoder to use serializing to a string; default is the :py:class:`OdinEncoder`.
        :param default_to_not_supplied: Used for loading partial resources. Any fields not supplied are replaced with
            NOT_SUPPLIED.

        """
        self.default_to_not_supplied = default_to_not_supplied
        self.encoder = encoder_cls(**kwargs)

    def loads(self, fp, resource_type=None, full_clean=True):
        """
        Load a document from a JSON encoded file.

        :param fp: a file pointer to read JSON data from.
        :param resource_type: A resource type, resource name or list of
            resources and names to use as the base for creating a resource. If
            a list is supplied the first item will be used if a resource type
            is not supplied.
        :param full_clean: Do a full clean of the object as part of the
            loading process.
        :returns: A resource object or object graph of resources loaded from file.

        """
        try:
            return resources.build_object_graph(
                json.loads(fp), resource_type, full_clean, False, self.default_to_not_supplied)
        except (ValueError, TypeError) as ex:
            raise CodecDecodeError(str(ex))

    def dump(self, resource, fp):
        """
        Dump to a JSON encoded file.

        :param resource: The root resource to dump to a JSON encoded file.
        :param fp: The file pointer that represents the output file.

        """
        try:
            # could accelerate with writelines in some versions of Python, at
            # a debuggability cost
            for chunk in self.encoder.iterencode(resource):
                fp.write(chunk)
        except ValueError as ex:
            raise CodecEncodeError(str(ex))

    def dumps(self, resource):
        """
        Dump to a JSON encoded string.

        :param resource: The root resource to dump to a JSON encoded file.
        :returns: JSON encoded string.

        """
        try:
            return self.encoder.encode(resource)
        except ValueError as ex:
            raise CodecEncodeError(str(ex))

_default_codec = JsonCodec()
load = _default_codec.load
loads = _default_codec.loads
dump = _default_codec.dump
dumps = _default_codec.dumps
