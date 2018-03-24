# -*- coding: utf-8 -*-
from __future__ import absolute_import
import uuid
import datetime
import os
from odin.datetimeutil import utc
from six import BytesIO
from odin.codecs import msgpack_codec
from .resources import *

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class TestMsgPackCodec(object):
    def test_dumps_and_loads(self):
        in_resource = IdentifiableBook(
            id=uuid.uuid4(),
            title='Consider Phlebas',
            isbn='0-333-45430-8',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
        )

        data = msgpack_codec.dumps(in_resource)
        out_resource = msgpack_codec.loads(data)

        assert out_resource.id == in_resource.id
        assert out_resource.title == in_resource.title
        assert out_resource.isbn == in_resource.isbn
        assert out_resource.num_pages == in_resource.num_pages
        assert out_resource.rrp == in_resource.rrp
        assert out_resource.fiction == in_resource.fiction
        assert out_resource.genre == in_resource.genre
        assert out_resource.authors[0].name == in_resource.authors[0].name
        assert out_resource.publisher.name == in_resource.publisher.name

    def test_dump_and_load_(self):
        in_resource = IdentifiableBook(
            id=uuid.uuid4(),
            title='Consider Phlebas',
            isbn='0-333-45430-8',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1, tzinfo=utc)]
        )

        fp = BytesIO()
        msgpack_codec.dump(in_resource, fp)

        fp.seek(0)
        out_resource = msgpack_codec.load(fp)

        assert out_resource.id == in_resource.id
        assert out_resource.title == in_resource.title
        assert out_resource.isbn == in_resource.isbn
        assert out_resource.num_pages == in_resource.num_pages
        assert out_resource.rrp == in_resource.rrp
        assert out_resource.fiction == in_resource.fiction
        assert out_resource.genre == in_resource.genre
        assert out_resource.authors[0].name == in_resource.authors[0].name
        assert out_resource.publisher.name == in_resource.publisher.name
        assert out_resource.published[0] == in_resource.published[0]
