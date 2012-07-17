#!/usr/bin/env python2
""" The Altium Format Parser """

# upconvert.py - A universal hardware design file format converter using
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


# Note: starting at 0x200 bytes, then 0x10200, 0x20200, etc., there is a 0x200-byte block starting
# with FD FF FF FF and then a series of sequential 4-byte values.  I don't know the purpose of
# these interrupting blocks, but when I read the file, I simply pass over them.  Disregarding them,
# here is the Altium schematic file structure:
# 
# FILE HEADERS (some contain unicode titles followed by unknown binary data)
# - 0x200 bytes whose meaning is yet unknown
# - 0x80 bytes for "Root Entry"
# - 0x80 bytes for "File Header"
# - 0x80 bytes for "Storage"
# - 0x80 bytes for "Additional"
# - 0x200 more unknown bytes 
#
# PARTS (sequential, variable number of parts, each having the following format)
#   - 4-byte little-endian integer describing the length of data to follow (including ending null)
#   - (length from above) bytes of data of the format |PROPERTY=VALUE
#      - except the "TEXT" property which seems to have "==" as its separator
#   - one null byte (0x00)
#
# FILE FOOTERS
# - Variable length of zero-padding following the last part
# - 0x600 bytes related to icon storage
# - 0x200 bytes for the last file footer

# The struct library makes it easy to read stored 4-byte integers.
import struct

from upconvert.core.design import Design


# This is the primary class.  Its members will be the various elements of an Altium schematic file.
class Altium:
    """ The Altium Format Parser """

    def __init__(self):
        self.last_header = None
        self.file_header = None
        self.first_header = None
        self.root_entry = None
        self.storage = None
        self.parts = None
        self.additional = None


    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is an altium schematic """
        with open(filename, 'r') as f:
            data = f.read()
        confidence = 0
        if 'altium' in data:
            confidence += 0.5
        return confidence


    # A simple string method to show off what has been parsed and stored.  It moves the easily-
    # identifiable blocks NAME and TEXT to the top of the printout for each part.
    def __str__(self):
        result = ""
        for part in self.parts:
            if "NAME" in part:
                result += "NAME: " + part["NAME"] + "\n"
            elif "TEXT" in part:
                result += "TEXT: " + part["TEXT"] + "\n"
            for key in part:
                if (key != "NAME") and (key != "TEXT"):
                    result += key + ": " + part[key] + "\n"
            result += "\n"
        return result


    def parse(self, file_path):
        """ Parse an Altium file into a design """
        design = Design()

        # Open the file in read-binary mode and only proceed if it was properly opened.
        in_file = open(file_path, "rb")
        if in_file:
            # Read the entire contents, omitting the interrupting blocks.
            input = in_file.read(0x200)
            # Skip the first 0x200 interrupting block.
            temp = in_file.read(0x200)
            while temp:
                # Read the next 0x10000 minus 0x200.
                temp = in_file.read(0xFE00)
                input += temp
                # Skip the next 0x200 interrupting block.
                temp = in_file.read(0x200)
            in_file.close()
            # Store all the headers, though they are not used.
            cursor_start = 0
            self.first_header = input[cursor_start:cursor_start+0x200]
            cursor_start += 0x200
            self.root_entry = input[cursor_start:cursor_start+0x80]
            cursor_start += 0x80
            self.file_header = input[cursor_start:cursor_start+0x80]
            cursor_start += 0x80
            self.storage = input[cursor_start:cursor_start+0x80]
            cursor_start += 0x80
            self.additional = input[cursor_start:cursor_start+0x80]
            cursor_start += 0x80
            self.last_header = input[cursor_start:cursor_start+0x200]
            cursor_start += 0x200
            # Now prepare to read each of the parts.  Initialize an "end" cursor.
            cursor_end = 0
            # Get the size of the next part block.
            next_size = struct.unpack("<I", input[cursor_start:cursor_start+4])[0]
            # Advance the "start" cursor.
            cursor_start += 4
            # Create a list to store all the parts.
            self.parts = []
            # Loop through until the "next size" is 0, which is the end of the parts list.
            while next_size != 0:
                cursor_end = input.find("\x00", cursor_start)
                # Create a dictionary to store all the property:value pairs.
                result = {}
                # Get a list of pairs by splitting on the separator character "|".
                property_list = input[cursor_start:cursor_end].split("|")
                # For each one, copy out whatever is before any "=" as property, and whatever is
                # after any "=" as value.
                for prop in property_list:
                    if prop:
                        property_val = p.split("=")[0]
                        # The negative list index is to handle the cases with "==" instead of "=".
                        value = p.split("=")[-1]
                        # Add the property to the result dictionary.
                        result[property_val] = value
                # Add the dictionary to the list of parts.
                self.parts.append(result)
                # Set things up for the next iteration of the loop.
                cursor_start = cursor_end + 1
                next_size = struct.unpack("<I", input[cursor_start:cursor_start+4])[0]
                cursor_start += 4
            # Here the footers could be found and stored, but I don't think they're important.

        return design
