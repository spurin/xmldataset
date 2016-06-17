.. :changelog:

History
-------

0.1.0 (2014-08-17)
++++++++++++++++++

* First release on PyPI.

0.1.1 (2014-08-17)
++++++++++++++++++

* Minor updates to supporting documents

0.1.2 (2014-08-17)
++++++++++++++++++

* Minor updates to supporting documents

0.1.3 (2014-08-17)
++++++++++++++++++

* Minor updates to supporting documents

0.1.4 (2014-08-27)
++++++++++++++++++

* Added default option to profile markup, allows a default value to be
  be set in the event that the context is missing from the XML, usage
  default:           Results in a string of '' for missing entries
  default:Missing    Results in a string of 'Missing' for missing entries

0.1.5 (2014-09-08)
++++++++++++++++++

* Added an option of __DATASET_PROCESSING__ which allows datasets
  to be processed against a function, usage
  __DATASET_PROCESSING__ = dataset:process

  The process needs to be parsed as an object parameter as per the
  existing dataset process functionality

0.1.6 (2014-09-24)
++++++++++++++++++

* Updated the default option so that it works with nested defaults

  If there is a level in the XML structure that is not
  traversed but contains defaults, we may still want these
  default values to be reflected in the dataset.  The parser
  now understands the optional syntax -

  __ALWAYS_FOLLOW__ entry

  To allow the parser to follow the profile entry and set defaults

0.1.7 (2015-06-02)
++++++++++++++++++

* Added an option for parse_using_profile of global_values

  When supplied as a dictionary, all entries in the dictionary
  are merged into new datasets.  For example -
  
  parse_using_profile(xml, profile, global_values = { 'location' : 'Chorleywood'})

1.0.0 (2016-06-18)
++++++++++++++++++

* First official release, revamped documentation
