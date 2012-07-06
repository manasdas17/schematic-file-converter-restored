import unicodedata

def stringify_attributes(attributes):
    attrs = {}
    for name, value in attributes.iteritems():
        try:
            attrs[name] = str(value)
        except UnicodeEncodeError:
            attrs[name] = unicodedata.normalize('NFKD', value)
    return attrs