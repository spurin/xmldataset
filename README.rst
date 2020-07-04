==================================
xmldataset: simple xml parsing 🗃️
==================================

.. image:: https://camo.githubusercontent.com/13c4e50d88df7178ae1882a203ed57b641674f94/68747470733a2f2f63646e2e7261776769742e636f6d2f73696e647265736f726875732f617765736f6d652f643733303566333864323966656437386661383536353265336136336531353464643865383832392f6d656469612f62616467652e737667
    :target: https://github.com/sindresorhus/awesome

.. image:: https://travis-ci.org/spurin/xmldataset.png?branch=master
    :target: https://travis-ci.org/spurin/xmldataset

.. image:: https://badge.fury.io/py/xmldataset.png
    :target: http://badge.fury.io/py/xmldataset

XML Dataset: simple xml parsing

.. image:: https://xmldataset.readthedocs.io/en/latest/_static/logo.jpg

* Documentation: https://xmldataset.readthedocs.io

A Python library that simplifies the extraction of datasets from XML content.

XML is a simple markup format. Whilst simple, extracting data of interest is often more complicated than it needs to be.

xmldataset addresses this through an easy to use plaintext declaration that follows the structure of the XML document. The declaration is indented, matching the XML structure, the data we are interested in is tagged against a dataset.

Features

* Handles missing data from the XML structure, if it’s missing in the XML it is not populated in the dataset
* Handles both XML Elements and Attributes using the plaintext collection schema (attributes are depicted as a sublevel of an element)
* Easy to rename XML attributes/elements during processing to meet your requirements
* Inline manipulation of XML content through the process mechanism
* Dispatch mechanism, allows datasets to be dispatched for every N instance to allow asynchronous processing
