""" Converts all attribute values to a string """

import unicodedata

def stringify_attributes(attributes):
    """ Converts all attribute values to a string """
    attrs = {}
    for name, value in attributes.iteritems():
        try:
            attrs[name] = str(value)
        except UnicodeEncodeError:
            attrs[name] = unicodedata.normalize('NFKD', value)
    return attrs