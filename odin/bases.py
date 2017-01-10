import abc
import six
import collections

from odin.exceptions import CodecError


class ResourceIterable(collections.Iterable):
    """
    Iterable object that yields resources.
    """
    @abc.abstractmethod
    def __iter__(self):
        while False:
            yield None


class TypedResourceIterable(ResourceIterable):
    """
    Iterable object that yields a specific resource.
    """
    def __init__(self, resource_type):
        self.resource_type = resource_type

    @abc.abstractmethod
    def __iter__(self):
        while False:
            yield None


class Codec(six.with_metaclass(abc.ABCMeta, object)):
    """
    Implementation of a codec for (de)serialisation of resources.
    """
    pass


class DocumentCodec(Codec):
    """
    A codec that loads an entire document (eg JSON)
    """
    def load(self, fp, resource=None, full_clean=True):
        """
        Load a resource from a file (or file like object)

        :param fp: File (or file like) object.
        :param resource: Optional resource to load (not required if file resources are specified)
        :type resource: odin.resources.ResourceBase
        :param full_clean: Perform a full clean on the resource.
        :rtype: odin.resources.ResourceBase | T <resource>

        """
        return self.loads(fp.read(), resource, full_clean)

    @abc.abstractmethod
    def loads(self, s, resource=None, full_clean=True):
        """
        Load a resource from a string.

        :param s: String
        :param resource: Optional resource to load (not required if file resources are specified)
        :type resource: odin.resources.ResourceBase
        :param full_clean: Perform a full clean on the resource.
        :rtype: odin.resources.ResourceBase | T <resource>

        """

    @abc.abstractmethod
    def dump(self, fp, resource):
        """
        Dump resource to a file (or file like object)

        :param fp: File (or file like) object.
        :param resource: Resource to dump
        :type resource: odin.resources.ResourceBase | ResourceIterable | array | dict

        """

    @abc.abstractmethod
    def dumps(self, resource):
        """
        Dump resource to a string

        :param resource: Resource to dump
        :type resource: odin.resources.ResourceBase | ResourceIterable | array | dict
        :rtype: str

        """


class IterableCodecWriter(object):
    @abc.abstractmethod
    def write(self, resource):
        pass


class IterableCodec(Codec):
    """
    A codec that loads data that can be iterated (eg CSV)
    """
    @staticmethod
    def _get_resource_type(resources, resource_type):
        if isinstance(resources, TypedResourceIterable):
            # Use first resource to obtain field list
            return resource_type or resources.resource_type
        elif isinstance(resources, ResourceIterable) and resource_type:
            return resource_type
        elif isinstance(resources, (list, tuple)):
            if not len(resources):
                return
            # Use first resource to obtain field list
            return resource_type or resources[0]
        else:
            raise CodecError("Resource type not defined.")

    @abc.abstractmethod
    def reader(self, fp, resource_type, full_clean=True):
        """
        Get an iterable resource reader for a file (or file like object)

        :param fp: File (or file like) object.
        :param resource_type: Resource to load
        :type resource_type: odin.resources.ResourceBase
        :param full_clean: Perform a full clean on the resource.
        :rtype: TypedResourceIterable(T<resource>)

        """
        pass

    @abc.abstractmethod
    def writer(self, fp, resource_type):
        """
        Get a writer object

        :param fp: File (or file like) object.
        :param resource_type: Resource to write
        :type resource_type: odin.resources.ResourceBase
        :rtype: IterableCodecWriter

        """
        pass

    def dump(self, fp, resources, resource_type=None):
        """
        Shortcut to write a collection of resources to a file (or file like object).

        :param fp: File (or file like) object.
        :param resources: Resource collection to write to file.
        :type resources: TypedResourceIterable | ResourceIterable | list | tuple
        :param resource_type: Resource to write
        :type resource_type: odin.resources.ResourceBase
        :rtype: IterableCodecWriter

        """
        resource_type = self._get_resource_type(resources, resource_type)
        writer = self.writer(fp, resource_type)
        map(writer.write, resources)

    def dumps(self, resources, resource_type=None):
        """
        Dump output to a string

        :param resources: Resource collection to write to file.
        :type resources: TypedResourceIterable | ResourceIterable | list | tuple
        :param resource_type: Resource to write
        :type resource_type: odin.resources.ResourceBase
        :rtype: str

        """
        buf = six.StringIO.StringIO()
        self.dump(buf, resources, resource_type)
        return buf.getvalue()
