#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

def yandex_date(string):
    return datetime.datetime.strptime(string[:-3] + string[-2:], "%Y-%m-%dT%H:%M:%S%z")

class YaAudienceObject(object):
    """
        Base class for all objects mirroring the ones returned by Yandex.Audience REST API.
        It must have a fixed number of fields, each field must have a type.
        It also supports subscripting and access of fields through the . operator.
        :param field_types: `dict` or `None`
    """

    def __init__(self, field_types=None):
        if field_types is None:
            field_types = {}

        self.FIELD_TYPES = {}
        self.FIELDS = {}
        self.set_field_types(field_types)

    def set_field_types(self, field_types):
        """
            Set the field types of the object
            :param field_types: `dict`, where keys are the field names and values are types (or factories)
        """

        self.FIELD_TYPES = field_types

        for field in field_types.keys():
            self[field] = None

    def set_field_type(self, field, type):
        """
            Set field type.
            :param field: `str`
            :param type: type or factory
        """

        self.FIELD_TYPES[field] = type
        self[field] = None

    def remove_field(self, field):
        """
            Remove field.
            :param field: `str`
        """

        self.FIELDS.pop(field)
        self.FIELD_TYPES.pop(field)

    def import_fields(self, source_dict):
        """
            Set all the fields of the object to the values in `source_dict`.
            All the other fields are ignored
            :param source_dict: `dict` or `None` (nothing will be done in that case)
        """

        if source_dict is not None:
            for field in self.FIELDS:
                try:
                    self[field] = source_dict[field]
                except KeyError:
                    pass

    def __setattr__(self, attr, value):
        if attr in ("FIELDS", "FIELD_TYPES"):
            self.__dict__[attr] = value
            return

        datatype = self.FIELD_TYPES[attr]
        self.FIELDS[attr] = datatype(value) if value is not None else None

    def __getattr__(self, attr):
        if attr in ("FIELDS", "FIELD_TYPES"):
            return self.__dict__[attr]

        return self.FIELDS[attr]

    def __getitem__(self, key):
        return self.FIELDS[key]

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __delitem__(self, key):
        del self.FIELDS[key]

    def __iter__(self):
        return iter(self.FIELDS)

    def __len__(self):
        return len(self.FIELDS)

    def __repr__(self):
        return "-----------------------------\n\r<%s%r>\n\r-----------------------------" % (self.__class__.__name__, self.FIELDS)




class SegmentObject(YaAudienceObject):
    """
        Segment information object.
        :param segment_info: `dict` or `None`
    """

    def __init__(self, segment_info=None):
        YaAudienceObject.__init__(self, {"id":                       int,
                                         "name":                     str,
                                         "type":                     str,
                                         "status":                   str,
                                         "create_time":              yandex_date,
                                         "owner":                    str,
                                         "has_guests":               bool,
                                         "guest_quantity":           int,
                                         "can_create_dependent":     bool,
                                         "has_derivatives":          bool,
                                         "cookies_matched_quantity": int,
                                         "hashed":                   bool,
                                         "content_type":             str,
                                         "item_quantity":            int,
                                         "valid_unique_quantity":    int,
                                         "valid_unique_percentage":  str,
                                         "matched_quantity":         int,
                                         "matched_percentage":       str,
                                         "counter_id":               int,
                                         "guest":                    bool})

        self.import_fields(segment_info)

class SegmentFileObject(YaAudienceObject):
    """
        Segment information object.
        :param segment_file_info: `dict` or `None`
    """

    def __init__(self, segment_file_info=None):
        YaAudienceObject.__init__(self, {"id":                       int,
                                         "type":                     str,
                                         "status":                   str,
                                         "has_guests":               bool,
                                         "guest_quantity":           int,
                                         "can_create_dependent":     bool,
                                         "has_derivatives":          bool,
                                         "cookies_matched_quantity": int,
                                         "hashed":                   bool,
                                         "item_quantity":            int,
                                         "guest":                    bool})

        self.import_fields(segment_file_info)
