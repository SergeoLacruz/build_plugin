[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Build plugin

This is plugin for [InvenTree](https://inventree.org), which provides support additional build
data. It adds a panel to the build details view. In this panel you can add relevant data
that are needed in case you wand to have PCBs manufactured by an external partner. Other
production relevant figures are extracted from the InvenTree database.

![build_plugin](https://github.com/SergeoLacruz/build_plugin/blob/main/pictures/build_panel.png)

The total number of components on the board is calculated by counting the parts in the BOM
of the part to build.

Codes in BOM is also taken from the BOM of the part to build

The PCB data requires a special structure of your database. There are always
two parts that belong together: the bare PCB and the populated PCB. These two
parts are linked using the related part property. The part you build is
a populated circuit board.

The plugin searches for the bare PCB. This one must have at least four parameters:
width, length, number of layers and a flag for double side assembly. These parameters
are properties of the bars PCB. So they are stored there. The name
of the parameters need to be configured in the plugin configuration. For this to work
you need to setup suppliers with contacts.

Additional data for manufacturing company, contact, ..., need to be set in the plugin UI.
These data is stored in the metadata area of the build when the Save button is pressed.
When the panel is initialized all data is loaded from the metadata field and available
for panel and report. So the panel always shows the actual data when it is displayed.

All parameters are exported to the report context using the report mixin. So a report can be
created. A simple report template is provided for a request for quotation that can be sent out
to the external partner.

![request fpr quotation](https://github.com/SergeoLacruz/build_plugin/blob/main/pictures/rfq.png)

Actually this is not finished but a good example for panel UI, data storage and reporting.

## Installation

There is no installation package yet. Just copy python and templates to src/inventree/plugins
and load the report template.

## Configuration Options

### PK of our Company
Here you can chose your company from the IvenTree database. This is used ad a sender in the
RFQ report.

### PK of parameters
Select here your parameters for the bare PCB.
