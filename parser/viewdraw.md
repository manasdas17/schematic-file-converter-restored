ViewDraw (and descendents) Schematic Parser
==========================================
As best I (Patrick Yeon) can tell, ViewDraw has been associated with ViewLogic, Innoveda Corp., and now with Mentor under their ePD and DxDesigner tools. The format, extended as needed, still shows up in some places in the latest version of DxDesigner I have seen, even though the iCDB is meant to be the project database.

This work is based off Stuart Brorson and Steven Salkow's earlier "ViewDraw File Formats" documentation, with Patrick Yeon working out further extended details based on ViewDraw output files strewn about online.

Current Status
--------------
The parser can make a decent attempt at parsing schematic and symbol data from old versions (schematic files with V 51, symbol files with V 50 or 51, that I've seen). It has no way to stitch together multi-page designs, and some details fall through the cracks because they haven't been worked into the upverter format (yet).

This parser has been developed with the [ml50x design files](http://www.xilinx.com/support/documentation/boards_and_kits/ml50x_schematics.zip)

Bugs, Omissions, and other Brokeness
------------------------------------
At the moment, probably a fair number.
* A few features of the ViewDraw format couldn't be fit into the upverter output format yet: part flipping and re-scaling, at least

Todo
----
In no particular order:
* Harden up against invalid input
* Work is likely required around pin numbering/naming
* Nets should be streamlined so that they use a minimum of points
* Test, test, test.

How To Help
-----------
I no longer have access to DxDesigner, so any design output to help shore up the understanding of this format would be helpful, especially if it is not currently handled properly or completely by the code. ViewDraw output from other tools/versions would also be helpful.

Further Notes
-------------
From a helpful viewdraw.ini, suspect this is about the `Q` command:

```
| Colors                                                                        
| ------------------------------------------------------------------            
|                                                                               
|  0  Black   |  4  Red       |   8  Gray       |  12  Lt. Red                  
|  1  Blue    |  5  Magenta   |   9  Lt. Blue   |  13  Lt. Magenta              
|  2  Green   |  6  Brown     |  10  Lt. Green  |  14  Yellow                   
|  3  Cyan    |  7  Lt. Gray  |  11  Lt. Cyan   |  15  White                    
|                                                                               
|                                                                               
| Fillstyles:                                                                   
| ------------------------------------------------------------------            
|                                                                               
|  0  Hollow  |  1  Solid                                                       
|                                                                               
|                                                                               
| Object        Color | Fillstyle | Linestyle                                   
|                     |  or Font  |             
```
