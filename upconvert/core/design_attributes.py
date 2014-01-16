#!/usr/bin/env python2
""" The attributes class """

# upconvert - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time
from upconvert.utils.stringify import stringify_attributes


class DesignAttributes:
    """ The DesignAttributes class corresponds to the design_attributes
    object in the Open JSON format """

    def __init__(self):
        self.annotations = []
        self.attributes = dict()
        self.metadata = Metadata()

    def add_annotation(self, annotation):
        """ Add an annotation """
        self.annotations.append(annotation)


    def add_attribute(self, key, value):
        """ Add an attribute """
        self.attributes[key] = value


    def set_metadata(self, metadata):
        """ Set the metadata """
        self.metadata = metadata


    def scale(self, factor):
        """ Scale the x & y coordinates of the design attributes. """
        for ann in self.annotations:
            ann.scale(factor)


    def json(self):
        """ Return the design attributes as JSON """
        return {
            "annotations" : [a.json() for a in self.annotations],
            "metadata" : self.metadata.json(),
            "attributes" : stringify_attributes(self.attributes),
            }


class Metadata:
    """ The metadata of a DesignAttributes object """

    def __init__(self):
        self.name = "" # TODO: make this name reflect the name from eagle
        self.license = "" # TODO: add license selection to upconvert.py
        self.owner = ""
        self.updated_timestamp = int(time.time())
        self.design_id = ""
        self.description = ""
        self.slug = self.name.replace(' ','-')
        self.attached_urls = list()


    def set_name(self, name):
        """ Set the name """
        self.name = name


    def set_license(self, lic):
        """ Set the licence """
        self.license = lic


    def set_owner(self, owner):
        """ Set the owner """
        self.owner = owner


    def set_updated_timestamp(self, updated_timestamp):
        """ Set the timestamp """
        self.updated_timestamp = int(updated_timestamp)


    def set_design_id(self, design_id):
        """ Set the design id """
        self.design_id = design_id


    def set_description(self, description):
        """ Set the description """
        self.description = description


    def set_slug(self, slug):
        """ Set the slug """
        self.slug = slug


    def add_attached_url(self, attached_url):
        """ Attach a url """
        self.attached_urls.append(attached_url)


    def json(self):
        """ Return the metadata as JSON """
        return {
            "name": self.name,
            "license": self.license,
            "owner": self.owner,
            "updated_timestamp": self.updated_timestamp,
            "design_id": self.design_id,
            "description": self.description,
            "slug": self.slug,
            "attached_urls": []
            }
