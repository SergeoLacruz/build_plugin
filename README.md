[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Build plugin

This is plugin for [InvenTree](https://inventree.org), which provides support additional build
data. It adds a panel to the build details view. Int this panel you can add relevant data
that are needed in case you wand to have PCBs manufactured by an external partner. All 
data is stored in the metadata area of the build. Additional data is exported to the 
report context using the report mixin.

A report template is provided that creates a request for quotation that can be sent out 
to the external partner. This RFQ is based on data in the InvenTree database and on additional
data from the plugin. So for the report to work you need to setup companies with addresses and 
contacts. 

Actually this is not finished but a good example for panel UI, data storage and reporting.

## Installation

Just copy python and templates to src/inventree/plugins and load the report template.
 
## Configuration Options

### PK of our Company 
Here you can chose your company from the IvenTree database. This is used ad a sender in the 
RFQ report. 

