.. complexity documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

xmldataset: simple xml parsing
======================================

.. toctree::
   :hidden:

A Python library that simplifies the extraction of datasets from XML content.

XML is a simple markup format.  Whilst simple, extracting data of interest is often more complicated than it needs to be.

**xmldataset** addresses this through an easy to use plaintext declaration that follows the structure of the XML document.  The declaration is indented, matching the XML structure, the data we are interested in is tagged against a dataset.

Take for example, an XML document that lists colleagues:

::

   # Declare XML
   xml = """<?xml version="1.0"?>
   <colleagues>
       <colleague>
           <title>The Boss</title>
           <phone>+1 202-663-9108</phone>
           <email>boss@the_company.com</email>
       </colleague>
       <colleague>
           <title>Admin Assistant</title>
           <phone>+1 347-999-5454</phone>
           <email>admin@the_company.com</email>
       </colleague>
       <colleague>
           <title>Minion</title>
           <phone>+1 792-123-4109</phone>
           <email>minion@the_company.com</email>
       </colleague>
   </colleagues>"""


To capture the title, email and phone for each colleague, it is simple, using xmldataset:

::

   import xmldataset

   # xmldataset declaration
   profile = """
   colleagues
       colleague
           title = dataset:colleagues
           phone = dataset:colleagues
           email = dataset:colleagues"""

   # Print the output
   print(xmldataset.parse_using_profile(xml, profile))

Resulting in the following output:

::

   {   'colleagues': [   {   'email': 'boss@the_company.com',
                             'phone': '+1 202-663-9108',
                             'title': 'The Boss'},
                         {   'email': 'admin@the_company.com',
                             'phone': '+1 347-999-5454',
                             'title': 'Admin Assistant'},
                         {   'email': 'minion@the_company.com',
                             'phone': '+1 792-123-4109',
                             'title': 'Minion'}]}

Features
--------

* Handles missing data from the XML structure, if it's missing in the XML it is not populated in the dataset
* Handles both XML Elements and Attributes using the plaintext collection schema (attributes are depicted as a sublevel of an element)
* Easy to rename XML attributes/elements during processing to meet your requirements
* Inline manipulation of XML content through the process mechanism
* Dispatch mechanism, allows datasets to be dispatched for every N instance to allow asynchronous processing


Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   contributing
   authors
   history

Contributors
============

``xmldataset`` is written and maintained by `James Spurin <https://github.com/james.spurin>`_,  The module stands on the shoulders of giants with it's use of ElementTree and cElementTree as the core XML parser.

Thanks go to the following for their feedback and improvements:

* KleinerNull
* keluc
