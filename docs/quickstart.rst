
Quickstart
==========


Hi, welcome to the quick-start tutorial.

Installing xmldataset
----------------------

Use pip to install xmldataset ::

   pip install xmldataset

Configuring xmldataset
----------------------

To get started, you need to import the xmldataset package :) ::

   import xmldataset

Configuring pretty print
------------------------

For these examples, it is worth using the pretty print module as this provides a great way of validating the returned results.  Configure this as follows:

::

   import pprint

   # Setup Pretty Printing
   ppsetup = pprint.PrettyPrinter(indent=4)
   pp = ppsetup.pprint

Adding XML content
------------------

We need some XML to work with, all of the examples will use the same XML although the profile will change to depict different behaviour.  Set the XML
up as follows:

::

   xml = """<?xml version="1.0"?>
     <catalog>
        <shop number="1">
           <book id="bk101">
              <author>Gambardella, Matthew</author>
              <title>XML Developer's Guide</title>
              <genre>Computer</genre>
              <price>44.95</price>
              <publish_date>2000-10-01</publish_date>
              <description>An in-depth look at creating applications 
              with XML.</description>
           </book>
           <book id="bk102">
              <author>Ralls, Kim</author>
              <title>Midnight Rain</title>
              <genre>Fantasy</genre>
              <price>5.95</price>
              <publish_date>2000-12-16</publish_date>
              <description>A former architect battles corporate zombies, 
              an evil sorceress, and her own childhood to become queen 
              of the world.</description>
           </book>
        </shop>
        <shop number="2">
           <book id="bk103">
              <author>Corets, Eva</author>
              <title>Maeve Ascendant</title>
              <genre>Fantasy</genre>
              <price>5.95</price>
              <publish_date>2000-11-17</publish_date>
              <description>After the collapse of a nanotechnology 
              society in England, the young survivors lay the 
              foundation for a new society.</description>
           </book>
           <book id="bk104">
              <author>Corets, Eva</author>
              <title>Oberon's Legacy</title>
              <genre>Fantasy</genre>
              <price>5.95</price>
              <publish_date>2001-03-10</publish_date>
              <description>In post-apocalypse England, the mysterious 
              agent known only as Oberon helps to create a new life 
              for the inhabitants of London. Sequel to Maeve 
              Ascendant.</description>
           </book>
        </shop>
     </catalog>"""

Example 1 - Extracting the title and author from the dataset
------------------------------------------------------------

Configure the profile, according to the XML, we need to step down past
the element catalog, shop and book before we reach author and title.

We can then specify that author and title are stored in the dataset **title_and_author**:

::

   profile="""
   catalog
       shop
           book
               author = dataset:title_and_author
               title  = dataset:title_and_author"""

Running this results in the following output:

::

   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'title': 'Midnight Rain'},
                               {   'author': 'Corets, Eva',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'title': "Oberon's Legacy"}]}

Example 2 - Working with multiple datasets
------------------------------------------

Let's say we want to expand our collection so that we also capture the
title and genre.  This can be done quite simply by updating the profile
to include an additional dataset for title and a definition for genre:

::

   profile="""
   catalog
       shop
           book
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre"""

With this executed, we now have an additional dataset of title_and_genre as
well as the original title_and_author:

::

   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                'title': "XML Developer's Guide"},
                            {   'author': 'Ralls, Kim',
                                'title': 'Midnight Rain'},
                            {   'author': 'Corets, Eva',
                                'title': 'Maeve Ascendant'},
                            {   'author': 'Corets, Eva',
                                'title': "Oberon's Legacy"}],
    'title_and_genre': [   {   'genre': 'Computer',
                               'title': "XML Developer's Guide"},
                           {   'genre': 'Fantasy', 'title': 'Midnight Rain'},
                           {   'genre': 'Fantasy', 'title': 'Maeve Ascendant'},
                           {   'genre': 'Fantasy', 'title': "Oberon's Legacy"}]}

Example 3 - Handling XML attributes
-----------------------------------

XML Attributes are treated in the profile as a sub level key/value in the profile. The following example depicts the inclusion of the attribute 'id' in the returned datasets. Note how id is indented under book and on the same level as author, title, genre etc:

::

   profile="""
   catalog
       shop
           book
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre"""

With the following output:

::

   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'id': 'bk101',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'id': 'bk102',
                                   'title': 'Midnight Rain'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk103',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk104',
                                   'title': "Oberon's Legacy"}],
       'title_and_genre': [   {   'genre': 'Computer',
                                  'id': 'bk101',
                                  'title': "XML Developer's Guide"},
                              {   'genre': 'Fantasy',
                                  'id': 'bk102',
                                  'title': 'Midnight Rain'},
                              {   'genre': 'Fantasy',
                                  'id': 'bk103',
                                  'title': 'Maeve Ascendant'},
                              {   'genre': 'Fantasy',
                                  'id': 'bk104',
                                  'title': "Oberon's Legacy"}]}

Example 4 - Using higher level data across datasets
---------------------------------------------------

Note how the 'number' attribute is at a higher level than the existing data that we have captured.  Owning to it's hierachial position, this data may be of relevence to the datasets formed below.

Information that is available at a higher level to that of the specified dataset information can be referenced and included in datasets using a combination of the external_dataset and __EXTERNAL_VALUE__ markers.

The external_dataset marker informs the parser to store the information for later use. It follows the format of external_dataset:<target> where <target> is a reference name that identifies the external store.

The __EXTERNAL_VALUE__ marker informs the parser to reference a value that is or will be stored externally. It follows the format of __EXTERNAL_VALUE__ = <external_store>:<external_value>:<target_dataset>

::

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre"""

Produces the following, n.b. the change of number for books 3 and 4 on each dataset:

::

   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'id': 'bk101',
                                   'number': '1',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'id': 'bk102',
                                   'number': '1',
                                   'title': 'Midnight Rain'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk103',
                                   'number': '2',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk104',
                                   'number': '2',
                                   'title': "Oberon's Legacy"}],
       'title_and_genre': [   {   'genre': 'Computer',
                                  'id': 'bk101',
                                  'number': '1',
                                  'title': "XML Developer's Guide"},
                              {   'genre': 'Fantasy',
                                  'id': 'bk102',
                                  'number': '1',
                                  'title': 'Midnight Rain'},
                              {   'genre': 'Fantasy',
                                  'id': 'bk103',
                                  'number': '2',
                                  'title': 'Maeve Ascendant'},
                              {   'genre': 'Fantasy',
                                  'id': 'bk104',
                                  'number': '2',
                                  'title': "Oberon's Legacy"}]}

Example 5 - Optional Dataset Parameters: name
---------------------------------------------

Dataset declarations can receive additional parameters through comma seperated inclusions. In this example the XML element of 'genre' is renamed to 'style' during processing using the name declaration.

::

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre,name:style
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre"""

Within the dataset title_and_genre, the keyword 'genre' is now changed to 'style':

::
   
   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'id': 'bk101',
                                   'number': '1',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'id': 'bk102',
                                   'number': '1',
                                   'title': 'Midnight Rain'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk103',
                                   'number': '2',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk104',
                                   'number': '2',
                                   'title': "Oberon's Legacy"}],
       'title_and_genre': [   {   'id': 'bk101',
                                  'number': '1',
                                  'style': 'Computer',
                                  'title': "XML Developer's Guide"},
                              {   'id': 'bk102',
                                  'number': '1',
                                  'style': 'Fantasy',
                                  'title': 'Midnight Rain'},
                              {   'id': 'bk103',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': 'Maeve Ascendant'},
                              {   'id': 'bk104',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': "Oberon's Legacy"}]}

Example 6 - Optional Dataset Parameters: prefix
-----------------------------------------------

The prefix declaration assigns a prefix to the assignment name, for example genre with a prefix of shop_information_ will become shop_information_genre

For consistency, in this example, the external information of name uses the additional optional parameter of :<override_name> as mentioned in Example 4 to override the external name

::

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               id     = dataset:title_and_author,prefix:shop_information_ dataset:title_and_genre,prefix:shop_information_
               author = dataset:title_and_author,prefix:shop_information_
               title  = dataset:title_and_author,prefix:shop_information_ dataset:title_and_genre,prefix:shop_information_,prefix:shop_information_
               genre  = dataset:title_and_genre,prefix:shop_information_
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author:shop_information_number shop_information:number:title_and_genre:shop_information_number"""


Resulting in the following:

::
   
   {   'title_and_author': [   {   'shop_information_author': 'Gambardella, Matthew',
                                   'shop_information_id': 'bk101',
                                   'shop_information_number': '1',
                                   'shop_information_title': "XML Developer's Guide"},
                               {   'shop_information_author': 'Ralls, Kim',
                                   'shop_information_id': 'bk102',
                                   'shop_information_number': '1',
                                   'shop_information_title': 'Midnight Rain'},
                               {   'shop_information_author': 'Corets, Eva',
                                   'shop_information_id': 'bk103',
                                   'shop_information_number': '2',
                                   'shop_information_title': 'Maeve Ascendant'},
                               {   'shop_information_author': 'Corets, Eva',
                                   'shop_information_id': 'bk104',
                                   'shop_information_number': '2',
                                   'shop_information_title': "Oberon's Legacy"}],
       'title_and_genre': [   {   'shop_information_genre': 'Computer',
                                  'shop_information_id': 'bk101',
                                  'shop_information_number': '1',
                                  'shop_information_title': "XML Developer's Guide"},
                              {   'shop_information_genre': 'Fantasy',
                                  'shop_information_id': 'bk102',
                                  'shop_information_number': '1',
                                  'shop_information_title': 'Midnight Rain'},
                              {   'shop_information_genre': 'Fantasy',
                                  'shop_information_id': 'bk103',
                                  'shop_information_number': '2',
                                  'shop_information_title': 'Maeve Ascendant'},
                              {   'shop_information_genre': 'Fantasy',
                                  'shop_information_id': 'bk104',
                                  'shop_information_number': '2',
                                  'shop_information_title': "Oberon's Legacy"}]}

Example 7 - Optional Dataset Parameters: process
------------------------------------------------

The process parameter can be used for inline manipulation of data. In this example the author is passed through a simple subroutine that returns an uppercase value.

The parser expects methods specified by the process to be passed by the parse_using_profile method as per the example:

::

   def to_upper(value):
       return value.upper()

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author,process:to_upper
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre,name:style
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre"""

   # Pretty Print the output
   output = xmldataset.parse_using_profile(xml,profile, process = { 'to_upper' : to_upper })
   pp(output)

We've specifically targetted the dataset title_and_author for the author value to be processed through **to_upper**:

::

   {   'title_and_author': [   {   'author': 'GAMBARDELLA, MATTHEW',
                                   'id': 'bk101',
                                   'number': '1',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'RALLS, KIM',
                                   'id': 'bk102',
                                   'number': '1',
                                   'title': 'Midnight Rain'},
                               {   'author': 'CORETS, EVA',
                                   'id': 'bk103',
                                   'number': '2',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'CORETS, EVA',
                                   'id': 'bk104',
                                   'number': '2',
                                   'title': "Oberon's Legacy"}],
       'title_and_genre': [   {   'id': 'bk101',
                                  'number': '1',
                                  'style': 'Computer',
                                  'title': "XML Developer's Guide"},
                              {   'id': 'bk102',
                                  'number': '1',
                                  'style': 'Fantasy',
                                  'title': 'Midnight Rain'},
                              {   'id': 'bk103',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': 'Maeve Ascendant'},
                              {   'id': 'bk104',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': "Oberon's Legacy"}]}

Example 8 - Hinting for new datasets
------------------------------------

During processing, the parser looks for indicators that it should create a new dataset. As an example, when new data is encountered rather than overriding the existing data, a new dataset is created. Unfortunately this may lead to unexpected results when working with poorly structured input where subsets of information may be missing from the XML structure.

To mitigate this, the hint __NEW_DATASET__ = <dataset> is available to force the creation of a new dataset upon entering a block.

If there are any concerns about the consistency of the XML document then it is recommended that the __NEW_DATASET__ declaration is made within all respective blocks as part of the profile definition.

::

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               __NEW_DATASET__ = title_and_author title_and_genre
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre,name:style
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre"""

Output as follows:

::

   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'id': 'bk101',
                                   'number': '1',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'id': 'bk102',
                                   'number': '1',
                                   'title': 'Midnight Rain'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk103',
                                   'number': '2',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk104',
                                   'number': '2',
                                   'title': "Oberon's Legacy"}],
       'title_and_genre': [   {   'id': 'bk101',
                                  'number': '1',
                                  'style': 'Computer',
                                  'title': "XML Developer's Guide"},
                              {   'id': 'bk102',
                                  'number': '1',
                                  'style': 'Fantasy',
                                  'title': 'Midnight Rain'},
                              {   'id': 'bk103',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': 'Maeve Ascendant'},
                              {   'id': 'bk104',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': "Oberon's Legacy"}]}

Example 9 - Dispatching datasets
--------------------------------

Datasets can be dispatched during processing.  This is beneficial especially where memory is concerned as the datasets can be handed off to another method and processed as opposed to filling up
memory before being returned.  The __generic__ keyword allows you to target all datasets:

::

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre,name:style
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre"""

   def print_dataset(value):
       pp(value)

   # Pretty Print the output
   output = xmldataset.parse_using_profile(xml,profile, dispatch = { 
           '__generic__' : { 
                   'counter' : 2, 
                   'coderef' : print_dataset 
           } 
   })


As the counter is set to 2, every dataset is passed as an object to the print_dataset method, note how each array now holds 2 entries:


::
   
   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'id': 'bk101',
                                   'number': '1',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'id': 'bk102',
                                   'number': '1',
                                   'title': 'Midnight Rain'}]}
   {   'title_and_genre': [   {   'id': 'bk101',
                                  'number': '1',
                                  'style': 'Computer',
                                  'title': "XML Developer's Guide"},
                              {   'id': 'bk102',
                                  'number': '1',
                                  'style': 'Fantasy',
                                  'title': 'Midnight Rain'}]}
   {   'title_and_genre': [   {   'id': 'bk103',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': 'Maeve Ascendant'},
                              {   'id': 'bk104',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': "Oberon's Legacy"}]}
   {   'title_and_author': [   {   'author': 'Corets, Eva',
                                   'id': 'bk103',
                                   'number': '2',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk104',
                                   'number': '2',
                                   'title': "Oberon's Legacy"}]}

Example 10 - Dispatching multiple datasets
------------------------------------------

It is possible to dispatch datasets to different methods or to specify dataset specific counters:

::

   profile="""
   catalog
       shop
           number     = external_dataset:shop_information
           book
               id     = dataset:title_and_author dataset:title_and_genre
               author = dataset:title_and_author
               title  = dataset:title_and_author dataset:title_and_genre
               genre  = dataset:title_and_genre,name:style
               __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre"""

   def print_dataset(value):
       pp(value)

   # Pretty Print the output
   output = xmldataset.parse_using_profile(xml,profile, dispatch = { 
           'title_and_author' : { 
                   'counter' : 2, 
                   'coderef' : print_dataset 
           }, 
           'title_and_genre' : { 
                   'counter' : 3, 
                   'coderef' : print_dataset 
           } 
   })


As the title_and_genre is now dispatching 3 datasets, it's final dump is of a single dataset for the remaining entry:

:: 

   {   'title_and_author': [   {   'author': 'Gambardella, Matthew',
                                   'id': 'bk101',
                                   'number': '1',
                                   'title': "XML Developer's Guide"},
                               {   'author': 'Ralls, Kim',
                                   'id': 'bk102',
                                   'number': '1',
                                   'title': 'Midnight Rain'}]}
   {   'title_and_genre': [   {   'id': 'bk101',
                                  'number': '1',
                                  'style': 'Computer',
                                  'title': "XML Developer's Guide"},
                              {   'id': 'bk102',
                                  'number': '1',
                                  'style': 'Fantasy',
                                  'title': 'Midnight Rain'},
                              {   'id': 'bk103',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': 'Maeve Ascendant'}]}
   {   'title_and_genre': [   {   'id': 'bk104',
                                  'number': '2',
                                  'style': 'Fantasy',
                                  'title': "Oberon's Legacy"}]}
   {   'title_and_author': [   {   'author': 'Corets, Eva',
                                   'id': 'bk103',
                                   'number': '2',
                                   'title': 'Maeve Ascendant'},
                               {   'author': 'Corets, Eva',
                                   'id': 'bk104',
                                   'number': '2',
                                   'title': "Oberon's Legacy"}]}

Example 11 - Using xmldataset as an input to pandas
------------------------------------------

Thanks to keluc for this one, xmldataset works well as an input to pandas with the from_records method

::

   result = xmldataset.parse_using_profile(xml, profile)
   df = pd.DataFrame.from_records(result['...'])
