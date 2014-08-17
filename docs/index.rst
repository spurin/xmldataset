.. complexity documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

xmldataset: xml parsing made easy
======================================

.. toctree::
   :hidden:

XML is a simple markup language that can be used to encode documents in both a human-readable and machine-readable format.  Yet, whilst it is simple, why aren't the means of gathering what we need from XML just as simple?

Although there are a variety of approaches for gathering data from XML, most require an intermediate understanding of Python.  This however, changes with the use of **xmldataset**.

**xmldataset** is designed to make the process of gathering your desired data into a Python structure as simple as possible through its plaintext collection schema, deliminated just like Python!

The parsing process is aided with the following:

* A simple plaintext collection schema that describes the XML, the content of interest and the dataset in which it should be placed.  Datasets are returned as python structures, essentially, a dictionary with the key as the dataset and within a list of datasets (dictionaries).

* Extendable options to to ensure that the data is collected into a dataset, just the way you want it.  If you're not happy with the element name in the XML schema, there's an option for that, if the data format does not meet your requirements, there's an option of inline processing to manipulate data on the fly.  Whilst simple, **xmldataset** also provides a variety of options that allow it to be extended past it's normal usage.

An example of xmldataset in use is as follows -

::

   import xmldataset
   import pprint

   # Setup Pretty Printing
   ppsetup = pprint.PrettyPrinter(indent=4)
   pp = ppsetup.pprint

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

   # Declare Profile
   profile = """
   colleagues
       colleague
           title = dataset:colleagues
           email = dataset:colleagues
           phone = dataset:colleagues"""

   # Capture the output
   output = xmldataset.parse_using_profile(xml, profile)

   # Pretty Print the output
   pp(output)

Which results in the following output:

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
* Dispatch mechanism, allows datasets to be dispatched for every N instance to allow asynchronous processing


Contents:

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   contributing
   authors
   history

Contributors
============

``xmldataset`` is written and maintained by `James Spurin <https://github.com/james.spurin>`_,  The module stands on the shoulders of giants with it's use of ElementTree and cElementTree as the core XML parser.  Thanks go to the team of ``dataset``, namely `Friedrich Lindenberg <https://github.com/pudo>`_, `Gregor Aisch <https://github.com/gka>`_ and `Stefan Wehrmeyer <https://github.com/stefanw>`_ who's influence is very prevelant in this sphinx documentation (and might I add, this module would work fantastically alongside dataset).  Thanks to Kenneth Reitz and Armin Ronacher for the Sphinx template.

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
