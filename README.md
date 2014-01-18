**WARNING:  Upverter is in the process of overhauling our UPV format to a new version.  We don't expect to maintain the current version, however we look forward to sharing our new version with you when it's ready to go!**


The Upverter Universal Format Converter
=======================================
A command line python anything-in anything-out file converter to go between the multitude of electrical circuit schematic file formats. This project was started by Upverter (http://upverter.com).

Folder Contents
---------------

* `upconvert/core/` - All of the converter code
* `doc/` - Everything related to documentation
* `upconvert/library/` - Library files for the software packages that dont export complete files
* `upconvert/parser/` - All of the in code
* `test/` - A set of test files for each format
* `upconvert/writer/` - All of the out code


Usage
---------------

```bash
usage: python2 -m upconvert.upconverter [-h] [-i INPUT] [-f TYPE] [-o OUTPUT] [-s SYMDIRS [SYMDIRS ...]] [-t TYPE]

optional arguments:
  -h, --help            show this help message and exit

  -i INPUT, --input INPUT
                        read INPUT file in
  -f TYPE, --from TYPE  read input file as TYPE

  -o OUTPUT, --output OUTPUT
                        write OUTPUT file out
  -t TYPE, --to TYPE    write output file as TYPE

  -s SYMDIRS [SYMDIRS ...], --sym-dirs SYMDIRS [SYMDIRS ...]
                        specify SYMDIRS to search for .sym files (for gEDA
                        only)

  --unsupported         run with an unsupported python version
  --raise-errors        show tracebacks for parsing and writing errors
  --profile             collect profiling information
  -v, --version         print version information and quit
  --formats             print supported formats and quit
```


Where to Get Help
---------------

```bash
python2 -m upconvert.upconverter -h
```

  Github: Submit an issue, or pull request.
  Email: support@upverter.com


Supported Formats
---------------

  The converter can import and export in the following popular open and closed source formats.

* Upverter OpenJSON
* KiCad
* gEDA
* Fritzing
* RS274-X Gerber (see note)
* NC Drill
* Eagle
* Eagle XML             (in testing)
* ViewDraw / DxDesigner (in testing)
* DSN                   (in testing)
* PNG Image
* Bill of Materials
* CSV Netlist
* Altium                (in development)
* Telesis Netlist       (in development)

Gerber Export Note:
Gerber export requires the arial.ttf font in the working directory the converter is run from.

Format Wish List
---------------

  This is the list of formats we wish we supported, and will work on or finish someday soon. We are looking for developers to help us so please ping us if you're interested!

* OrCad
* Existing supported formats - layout data
* DipTrace


The Concept
---------------

  To use an Upverter Open JSON export in another piece of software, you will need to convert it into that software's proprietary format. Likewise, to get your data out of another piece of software and import it into Upverter, you will also need to run their export through the converter. We are working to make this easier, but we will largely depend on community contribution and the participation of the other vendors.


Interchange Format Documentation
---------------

  The converter is based on the Upverter Open JSON Format fully documented at http://support.upverter.com/customer/portal/articles/553504-documentation-for-open-json-format. We hope that someday all of the major providers of schematic capture software will support interoperability with open formats like this one.


Key Contributors
---------------

  The converter has been an ongoing project since mid-2011 made up of many, many contributions by a team of distributed developers associated by little more than our desire to fix what we see as the horribly broken world of ECAD interoperability. The key contributors are as follows:

* jdavisp3    -  KiCad, Fritzing, EagleXML, Stability
* elbaschid   -  gEDA
* iparshin    -  EagleBin
* foobarmus   -  Gerber
* patrickyeon -  ViewDraw, Image
* machinaut   -  OpenJSON, Architecture


Licence
---------------

  http://www.apache.org/licenses/LICENSE-2.0.html
