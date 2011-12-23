The Upverter Universal Format Converter
=======================================
A command line python anything-in anything-out file converter to go between the multitude of electrical circuit schematic file formats. This project was started by Alex Ray (ajray@ncsu.edu), on behalf of Upverter (http://upverter.com).


Folder Contents
---------------

* `core/` - All of the converter code
* `doc/` - Everything related to documentation
* `example/` - Examples of input and output files
* `parser/` - All of the in code
* `test/` - A set of test files for each format
* `writer/` - All of the out code


Usage
---------------

```bash
usage: upconvert.py [-h] [-i INPUT] [-f TYPE] [-o OUTPUT] [-t TYPE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        read INPUT file in
  -f TYPE, --from TYPE  read input file as TYPE
  -o OUTPUT, --output OUTPUT
                        write OUTPUT file out
  -t TYPE, --to TYPE    write output file as TYPE
```


Where to Get Help
---------------

```bash
./upconvert.py -h
```


Supported Formats
---------------

  The converter started with support for KiCad. We have since been expanding it to support many of the popular open and closed source formats, as follows.

* KiCad     (in beta testing)
* gEDA      (in beta testing)
* Eagle     (in alpha testing)
* Eagle XML (in alpha testing)
* Fritzing  (in development)
* Altium    (in development)
* Gerber    (in development)


Format Wish List
---------------

  This is the list of formats we wish we supported, and will work on someday (hopefully soon!). We are looking for developers to help us so please ping us if you're interested!

* DXDesigner
* PADs
* Alegro
* OrCad
* DSN


Exports
---------------

  This is the list of formats we can export too, given an import with the required info in it. These are currently all in development.

* BOM (Bill of Materials) in CSV format
* Netlist in CSV format
* Netlist in Telesis format
* Layout Data in RS274-X (Gerber) format
* Drill Data in Excellon format


The Concept
---------------

  To use an Upverter Open JSON export in another piece of software, you will need to convert it into that software's proprietary format. Likewise, to get your data out of another piece of software and import it into Upverter, you will also need to run their export through the converter. We are working to make this easier, but we will largely depend on community contribution and the participation of the other vendors.


Interchange Format Documentation
---------------

  The converter is based on the Upverter Open JSON Format fully documented at http://upverter.com/resources/open-json-format/. We hope that someday all of the major providers of schematic capture software will support interoperability with open formats like this one.
