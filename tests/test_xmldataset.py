#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xmldataset
----------------------------------

Tests for `xmldataset` module.
"""

try:
   import unittest2 as unittest
except ImportError:
   import unittest

from xmldataset import parse_using_profile

class TestImports(unittest.TestCase):
    ''' Tests imports '''

    def test_import_parse_using_profile(self):
        try:
            from xmldataset import parse_using_profile
            pass
        except:
            raise Exception('Failed to import parse_using_profile')

    def test_dict_equal(self):
            self.assertDictEqual({'name' : 'james'}, {'name' : 'james'})

class TestCreateObject(unittest.TestCase):

    def setUp(self):

        # ------------------------------------------------------------------------------
        #    Define XML
        # ------------------------------------------------------------------------------
        self.xml = """<?xml version="1.0"?>
<catalog>
   <lowest number="123">
      <specificbefore>
         <specificvalue>123</specificvalue>
      </specificbefore>
      <book id="bk101">
         <optionalexternalstart>
            <externaldata>external_value1</externaldata>
         </optionalexternalstart>
         <author>Gambardella, Matthew</author>
         <title>XML Developer's Guide</title>
         <genre>Computer</genre>
         <price>44.95</price>
         <publish_date>2000-10-01</publish_date>
         <description>An in-depth look at creating applications
         with XML.</description>
         <optionalexternalend>
            <externaldata>external_value1</externaldata>
         </optionalexternalend>
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
      <book id="bk103">
         <optionalexternalstart>
            <externaldata>external_value2</externaldata>
         </optionalexternalstart>
         <author>Corets, Eva</author>
         <title>Maeve Ascendant</title>
         <genre>Fantasy</genre>
         <price>5.95</price>
         <publish_date>2000-11-17</publish_date>
         <description>After the collapse of a nanotechnology
         society in England, the young survivors lay the
         foundation for a new society.</description>
         <optionalexternalend>
            <externaldata>external_value2</externaldata>
         </optionalexternalend>
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
      <book id="bk105">
         <optionalexternalstart>
            <externaldata>external_value3</externaldata>
         </optionalexternalstart>
         <author>Corets, Eva</author>
         <title>The Sundered Grail</title>
         <genre>Fantasy</genre>
         <price>5.95</price>
         <publish_date>2001-09-10</publish_date>
         <description>The two daughters of Maeve, half-sisters,
         battle one another for control of England. Sequel to
         Oberon's Legacy.</description>
         <optionalexternalend>
            <externaldata>external_value3</externaldata>
         </optionalexternalend>
      </book>
      <book id="bk106">
         <author>Randall, Cynthia</author>
         <title>Lover Birds</title>
         <genre>Romance</genre>
         <price>4.95</price>
         <publish_date>2000-09-02</publish_date>
         <description>When Carla meets Paul at an ornithology
         conference, tempers fly as feathers get ruffled.</description>
      </book>
      <book id="bk107">
         <optionalexternalstart>
            <externaldata>external_value4</externaldata>
         </optionalexternalstart>
         <author>Thurman, Paula</author>
         <title>Splish Splash</title>
         <genre>Romance</genre>
         <price>4.95</price>
         <publish_date>2000-11-02</publish_date>
         <description>A deep sea diver finds true love twenty
         thousand leagues beneath the sea.</description>
         <optionalexternalend>
            <externaldata>external_value4</externaldata>
         </optionalexternalend>
      </book>
      <book id="bk108">
         <author>Knorr, Stefan</author>
         <title>Creepy Crawlies</title>
         <genre>Horror</genre>
         <price>4.95</price>
         <publish_date>2000-12-06</publish_date>
         <description>An anthology of horror stories about roaches,
         centipedes, scorpions  and other insects.</description>
      </book>
      <book id="bk109">
         <optionalexternalstart>
            <externaldata>external_value5</externaldata>
         </optionalexternalstart>
         <author>Kress, Peter</author>
         <title>Paradox Lost</title>
         <genre>Science Fiction</genre>
         <price>6.95</price>
         <publish_date>2000-11-02</publish_date>
         <description>After an inadvertant trip through a Heisenberg
         Uncertainty Device, James Salway discovers the problems
         of being quantum.</description>
         <optionalexternalend>
            <externaldata>external_value5</externaldata>
         </optionalexternalend>
      </book>
      <book id="bk110">
         <author>O'Brien, Tim</author>
         <title>Microsoft .NET: The Programming Bible</title>
         <genre>Computer</genre>
         <price>36.95</price>
         <publish_date>2000-12-09</publish_date>
         <description>Microsoft's .NET initiative is explored in
         detail in this deep programmer's reference.</description>
      </book>
      <book id="bk111">
         <optionalexternalstart>
            <externaldata>external_value6</externaldata>
         </optionalexternalstart>
         <author>O'Brien, Tim</author>
         <title>MSXML3: A Comprehensive Guide</title>
         <genre>Computer</genre>
         <price>36.95</price>
         <publish_date>2000-12-01</publish_date>
         <description>The Microsoft MSXML3 parser is covered in
         detail, with attention to XML DOM interfaces, XSLT processing,
         SAX and more.</description>
         <optionalexternalend>
            <externaldata>external_value6</externaldata>
         </optionalexternalend>
      </book>
      <book id="bk112">
         <author>Galos, Mike</author>
         <title>Visual Studio 7: A Comprehensive Guide</title>
         <genre>Computer</genre>
         <price>49.95</price>
         <publish_date>2001-04-16</publish_date>
         <description>Microsoft Visual Studio 7 is explored in depth,
         looking at how Visual Basic, Visual C++, C#, and ASP+ are
         integrated into a comprehensive development
         environment.</description>
      </book>
      <book2 id="bk200">
         <author>Grinberg, M</author>
         <title>Flask Web Development</title>
         <genre>Computer</genre>
         <price>29.95</price>
         <publish_date>2012-00-00</publish_date>
         <description>Flask Development in Python</description>
      </book2>
      <specificafter>
         <specificvalue>123</specificvalue>
      </specificafter>
   </lowest>
</catalog>"""

    def test_single_dataset(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_multi_datasets(self):

        profile = """catalog
        lowest
                book
                   id     = dataset:1
                   author = dataset:1 dataset:2
                   title  = dataset:1 dataset:2
                   genre  = dataset:1
                   price  = dataset:1 dataset:2
                   publish_date = dataset:1
                   description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}],
         '2': [{'author': 'Gambardella, Matthew',
                 'price': '44.95',
                 'title': "XML Developer's Guide"},
                 {'author': 'Ralls, Kim', 'price': '5.95', 'title': 'Midnight Rain'},
                 {'author': 'Corets, Eva', 'price': '5.95', 'title': 'Maeve Ascendant'},
                 {'author': 'Corets, Eva', 'price': '5.95', 'title': "Oberon's Legacy"},
                 {'author': 'Corets, Eva',
                 'price': '5.95',
                 'title': 'The Sundered Grail'},
                 {'author': 'Randall, Cynthia',
                 'price': '4.95',
                 'title': 'Lover Birds'},
                 {'author': 'Thurman, Paula',
                 'price': '4.95',
                 'title': 'Splish Splash'},
                 {'author': 'Knorr, Stefan',
                 'price': '4.95',
                 'title': 'Creepy Crawlies'},
                 {'author': 'Kress, Peter', 'price': '6.95', 'title': 'Paradox Lost'},
                 {'author': "O'Brien, Tim",
                 'price': '36.95',
                 'title': 'Microsoft .NET: The Programming Bible'},
                 {'author': "O'Brien, Tim",
                 'price': '36.95',
                 'title': 'MSXML3: A Comprehensive Guide'},
                 {'author': 'Galos, Mike',
                 'price': '49.95',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_multi_datasets_forced_new(self):

        profile = """catalog
        lowest
                book
                   __NEW_DATASET__ = 1 2
                   id     = dataset:1
                   author = dataset:1 dataset:2
                   title  = dataset:1 dataset:2
                   genre  = dataset:1
                   price  = dataset:1 dataset:2
                   publish_date = dataset:1
                   description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}],
         '2': [{'author': 'Gambardella, Matthew',
                 'price': '44.95',
                 'title': "XML Developer's Guide"},
                 {'author': 'Ralls, Kim', 'price': '5.95', 'title': 'Midnight Rain'},
                 {'author': 'Corets, Eva', 'price': '5.95', 'title': 'Maeve Ascendant'},
                 {'author': 'Corets, Eva', 'price': '5.95', 'title': "Oberon's Legacy"},
                 {'author': 'Corets, Eva',
                 'price': '5.95',
                 'title': 'The Sundered Grail'},
                 {'author': 'Randall, Cynthia',
                 'price': '4.95',
                 'title': 'Lover Birds'},
                 {'author': 'Thurman, Paula',
                 'price': '4.95',
                 'title': 'Splish Splash'},
                 {'author': 'Knorr, Stefan',
                 'price': '4.95',
                 'title': 'Creepy Crawlies'},
                 {'author': 'Kress, Peter', 'price': '6.95', 'title': 'Paradox Lost'},
                 {'author': "O'Brien, Tim",
                 'price': '36.95',
                 'title': 'Microsoft .NET: The Programming Bible'},
                 {'author': "O'Brien, Tim",
                 'price': '36.95',
                 'title': 'MSXML3: A Comprehensive Guide'},
                 {'author': 'Galos, Mike',
                 'price': '49.95',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_external_data(self):

        profile = """catalog
        lowest
            number = external_dataset:__external_value__1
            book
                id     = dataset:1
                author = dataset:1 dataset:2
                title  = dataset:1 dataset:2
                genre  = dataset:1
                price  = dataset:1 dataset:2
                publish_date = dataset:1
                description  = dataset:1
                __EXTERNAL_VALUE__ = __external_value__1:number:1 __external_value__1:number:2"""

        expected = {'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'number': '123',
          'price': '44.95',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'number': '123',
          'price': '5.95',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'number': '123',
          'price': '5.95',
          'publish_date': '2000-11-17',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'number': '123',
          'price': '5.95',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'number': '123',
          'price': '5.95',
          'publish_date': '2001-09-10',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-11-02',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'number': '123',
          'price': '6.95',
          'publish_date': '2000-11-02',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'number': '123',
          'price': '36.95',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'number': '123',
          'price': '36.95',
          'publish_date': '2000-12-01',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'number': '123',
          'price': '49.95',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}],
   '2': [{'author': 'Gambardella, Matthew',
          'number': '123',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'number': '123',
          'price': '5.95',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'number': '123',
          'price': '4.95',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'number': '123',
          'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'number': '123',
          'price': '4.95',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'number': '123',
          'price': '6.95',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'number': '123',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_custom_name(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = dataset:1,name:category
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'category': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'category': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'category': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'category': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'category': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'category': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'category': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'category': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'category': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'category': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'category': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'category': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_external_data_custom_name(self):

        profile = """catalog
        lowest
            number = external_dataset:__external_value__1
            book
                id     = dataset:1
                author = dataset:1 dataset:2
                title  = dataset:1 dataset:2
                genre  = dataset:1
                price  = dataset:1 dataset:2
                publish_date = dataset:1
                description  = dataset:1
                __EXTERNAL_VALUE__ = __external_value__1:number:1:numberx __external_value__1:number:2:numbery"""

        expected = {'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'numberx': '123',
          'price': '44.95',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'numberx': '123',
          'price': '5.95',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'numberx': '123',
          'price': '5.95',
          'publish_date': '2000-11-17',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'numberx': '123',
          'price': '5.95',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'numberx': '123',
          'price': '5.95',
          'publish_date': '2001-09-10',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'numberx': '123',
          'price': '4.95',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'numberx': '123',
          'price': '4.95',
          'publish_date': '2000-11-02',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'numberx': '123',
          'price': '4.95',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'numberx': '123',
          'price': '6.95',
          'publish_date': '2000-11-02',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'numberx': '123',
          'price': '36.95',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'numberx': '123',
          'price': '36.95',
          'publish_date': '2000-12-01',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'numberx': '123',
          'price': '49.95',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}],
   '2': [{'author': 'Gambardella, Matthew',
          'numbery': '123',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'numbery': '123',
          'price': '5.95',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'numbery': '123',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'numbery': '123',
          'price': '5.95',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'numbery': '123',
          'price': '5.95',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'numbery': '123',
          'price': '4.95',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'numbery': '123',
          'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'numbery': '123',
          'price': '4.95',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'numbery': '123',
          'price': '6.95',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'numbery': '123',
          'price': '36.95',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'numbery': '123',
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'numbery': '123',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_xgnore(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = __IGNORE__
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_xgnore_block(self):

        profile = """catalog
        lowest
                book = __IGNORE__
                book2
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = __IGNORE__
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {'1': [{'author': 'Grinberg, M',
         'description': 'Flask Development in Python',
         'id': 'bk200',
         'price': '29.95',
         'publish_date': '2012-00-00',
         'title': 'Flask Web Development'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_process(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1,process:to_upper
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'GAMBARDELLA, MATTHEW',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'RALLS, KIM',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'CORETS, EVA',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'CORETS, EVA',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'CORETS, EVA',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'RANDALL, CYNTHIA',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'THURMAN, PAULA',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'KNORR, STEFAN',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'KRESS, PETER',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'BRIEN, TIM",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'BRIEN, TIM",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'GALOS, MIKE',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        def to_upper(value):
           return value.upper()

        output = parse_using_profile(self.xml, profile, process = { 'to_upper' : to_upper } )
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_no_processes_supplied(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1,process:to_upper
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        with self.assertRaisesRegexp(Exception, 'process definition not supplied as argument'):
            parse_using_profile(self.xml, profile)

    def test_incorrect_process(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1,process:to_upper
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        def nullpass():
            pass

        with self.assertRaisesRegexp(Exception, 'process coderef to_upper missing'):
                parse_using_profile(self.xml, profile, process = { 'not_to_upper' : nullpass })

    def test_dispatch_all(self):

        profile = """catalog
        lowest
                book
                   id     = dataset:1
                   author = dataset:1 dataset:2
                   title  = dataset:1 dataset:2
                   genre  = dataset:1
                   price  = dataset:1 dataset:2
                   publish_date = dataset:1
                   description  = dataset:1"""

        expected = {'1_response': {'1': [{'author': 'Gambardella, Matthew',
                        'description': 'An in-depth look at creating applications\n         with XML.',
                        'genre': 'Computer',
                        'id': 'bk101',
                        'price': '44.95',
                        'publish_date': '2000-10-01',
                        'title': "XML Developer's Guide"},
                       {'author': 'Ralls, Kim',
                       'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                        'genre': 'Fantasy',
                        'id': 'bk102',
                        'price': '5.95',
                        'publish_date': '2000-12-16',
                        'title': 'Midnight Rain'},
                       {'author': 'Corets, Eva',
                       'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                        'genre': 'Fantasy',
                        'id': 'bk103',
                        'price': '5.95',
                        'publish_date': '2000-11-17',
                        'title': 'Maeve Ascendant'},
                      {'author': 'Corets, Eva',
                        'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                        'genre': 'Fantasy',
                        'id': 'bk104',
                        'price': '5.95',
                        'publish_date': '2001-03-10',
                        'title': "Oberon's Legacy"},
                      {'author': 'Corets, Eva',
                        'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                        'genre': 'Fantasy',
                        'id': 'bk105',
                        'price': '5.95',
                        'publish_date': '2001-09-10',
                        'title': 'The Sundered Grail'},
                       {'author': 'Randall, Cynthia',
                        'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                        'genre': 'Romance',
                        'id': 'bk106',
                        'price': '4.95',
                        'publish_date': '2000-09-02',
                        'title': 'Lover Birds'},
                       {'author': 'Thurman, Paula',
                        'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                        'genre': 'Romance',
                        'id': 'bk107',
                        'price': '4.95',
                       'publish_date': '2000-11-02',
                        'title': 'Splish Splash'},
                       {'author': 'Knorr, Stefan',
                        'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                        'genre': 'Horror',
                        'id': 'bk108',
                        'price': '4.95',
                        'publish_date': '2000-12-06',
                       'title': 'Creepy Crawlies'},
                       {'author': 'Kress, Peter',
                       'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                        'genre': 'Science Fiction',
                        'id': 'bk109',
                        'price': '6.95',
                        'publish_date': '2000-11-02',
                        'title': 'Paradox Lost'},
                       {'author': "O'Brien, Tim",
                        'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                        'genre': 'Computer',
                        'id': 'bk110',
                        'price': '36.95',
                        'publish_date': '2000-12-09',
                        'title': 'Microsoft .NET: The Programming Bible'},
                       {'author': "O'Brien, Tim",
                        'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                        'genre': 'Computer',
                        'id': 'bk111',
                        'price': '36.95',
                        'publish_date': '2000-12-01',
                        'title': 'MSXML3: A Comprehensive Guide'},
                       {'author': 'Galos, Mike',
                        'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                        'genre': 'Computer',
                        'id': 'bk112',
                        'price': '49.95',
                        'publish_date': '2001-04-16',
                        'title': 'Visual Studio 7: A Comprehensive Guide'}]},
  '2_response': {'2': [{'author': 'Gambardella, Matthew',
                        'price': '44.95',
                        'title': "XML Developer's Guide"},
                       {'author': 'Ralls, Kim',
                        'price': '5.95',
                        'title': 'Midnight Rain'},
                       {'author': 'Corets, Eva',
                        'price': '5.95',
                        'title': 'Maeve Ascendant'},
                       {'author': 'Corets, Eva',
                        'price': '5.95',
                        'title': "Oberon's Legacy"},
                       {'author': 'Corets, Eva',
                        'price': '5.95',
                        'title': 'The Sundered Grail'},
                       {'author': 'Randall, Cynthia',
                        'price': '4.95',
                        'title': 'Lover Birds'},
                       {'author': 'Thurman, Paula',
                        'price': '4.95',
                        'title': 'Splish Splash'},
                       {'author': 'Knorr, Stefan',
                        'price': '4.95',
                        'title': 'Creepy Crawlies'},
                       {'author': 'Kress, Peter',
                        'price': '6.95',
                        'title': 'Paradox Lost'},
                       {'author': "O'Brien, Tim",
                        'price': '36.95',
                        'title': 'Microsoft .NET: The Programming Bible'},
                       {'author': "O'Brien, Tim",
                        'price': '36.95',
                        'title': 'MSXML3: A Comprehensive Guide'},
                       {'author': 'Galos, Mike',
                        'price': '49.95',
                        'title': 'Visual Studio 7: A Comprehensive Guide'}]}}


        dataset1_holder = {}

        def dataset1(dataset):
           if '1' in dataset:
              dataset1_holder['1_response'] = dataset
           elif '2' in dataset:
              dataset1_holder['2_response'] = dataset

           #dataset1_holder['result'].append(dataset)
           #dataset1_holder.append(dataset)

        output = parse_using_profile(self.xml, profile, dispatch = { '__generic__' : { 'coderef' : dataset1, 'counter' : 100 } } )
        self.maxDiff = None
        self.assertEqual(expected, dataset1_holder)

    def test_dispatch_all_2s(self):

        profile = """catalog
        lowest
                book
                   id     = dataset:1
                   author = dataset:1 dataset:2
                   title  = dataset:1 dataset:2
                   genre  = dataset:1
                   price  = dataset:1 dataset:2
                   publish_date = dataset:1
                   description  = dataset:1"""

        expected1 = [{'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'price': '44.95',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'price': '5.95',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'}]},
  {'1': [{'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'price': '5.95',
          'publish_date': '2000-11-17',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'price': '5.95',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"}]},
  {'1': [{'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'price': '5.95',
          'publish_date': '2001-09-10',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'price': '4.95',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'}]},
  {'1': [{'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'price': '4.95',
          'publish_date': '2000-11-02',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'price': '4.95',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'}]},
  {'1': [{'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'price': '6.95',
          'publish_date': '2000-11-02',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'price': '36.95',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'}]},
  {'1': [{'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'price': '36.95',
          'publish_date': '2000-12-01',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'price': '49.95',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}]

        expected2 = [{'2': [{'author': 'Gambardella, Matthew',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim', 'price': '5.95', 'title': 'Midnight Rain'}]},
 {'2': [{'author': 'Corets, Eva',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'price': '5.95',
          'title': "Oberon's Legacy"}]},
  {'2': [{'author': 'Corets, Eva',
          'price': '5.95',
         'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'price': '4.95',
          'title': 'Lover Birds'}]},
  {'2': [{'author': 'Thurman, Paula',
         'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'price': '4.95',
          'title': 'Creepy Crawlies'}]},
  {'2': [{'author': 'Kress, Peter', 'price': '6.95', 'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'price': '36.95',
         'title': 'Microsoft .NET: The Programming Bible'}]},
  {'2': [{'author': "O'Brien, Tim",
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}]

        dataset1_holder = []
        dataset2_holder = []

        def dataset1(dataset):
           dataset1_holder.append(dataset)

        def dataset2(dataset):
           dataset2_holder.append(dataset)

        output = parse_using_profile(self.xml, profile, dispatch = { '1' : { 'coderef' : dataset1, 'counter' : 2 }, '2' : { 'coderef' : dataset2, 'counter' : 2 } } )

        self.maxDiff = None
        self.assertEqual(expected1, dataset1_holder)
        self.assertEqual(expected2, dataset2_holder)

    def test_external_data_before(self):

        profile = """catalog
        lowest
            number = external_dataset:__external_value__1
            specificbefore
                specificvalue = external_dataset:__external_value__1
            book
                id     = dataset:1
                author = dataset:1 dataset:2
                title  = dataset:1 dataset:2
                genre  = dataset:1
                price  = dataset:1 dataset:2
                publish_date = dataset:1
                description  = dataset:1
                __EXTERNAL_VALUE__ = __external_value__1:number:1 __external_value__1:number:2 __external_value__1:specificvalue:1"""

        expected = {'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'number': '123',
          'price': '44.95',
          'specificvalue': '123',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2000-11-17',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2001-09-10',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'number': '123',
          'price': '4.95',
          'specificvalue': '123',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'number': '123',
          'price': '4.95',
          'specificvalue': '123',
          'publish_date': '2000-11-02',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'number': '123',
          'price': '4.95',
          'specificvalue': '123',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'number': '123',
          'price': '6.95',
          'specificvalue': '123',
          'publish_date': '2000-11-02',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'number': '123',
          'price': '36.95',
          'specificvalue': '123',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'number': '123',
          'price': '36.95',
          'specificvalue': '123',
          'publish_date': '2000-12-01',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'number': '123',
          'price': '49.95',
          'specificvalue': '123',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}],
   '2': [{'author': 'Gambardella, Matthew',
          'number': '123',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'number': '123',
          'price': '5.95',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'number': '123',
          'price': '4.95',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'number': '123',
          'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'number': '123',
          'price': '4.95',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'number': '123',
          'price': '6.95',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'number': '123',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_external_data_after(self):

        profile = """catalog
        lowest
            number = external_dataset:__external_value__1
            specificafter
                specificvalue = external_dataset:__external_value__1
            book
                id     = dataset:1
                author = dataset:1 dataset:2
                title  = dataset:1 dataset:2
                genre  = dataset:1
                price  = dataset:1 dataset:2
                publish_date = dataset:1
                description  = dataset:1
                __EXTERNAL_VALUE__ = __external_value__1:number:1 __external_value__1:number:2 __external_value__1:specificvalue:1"""

        expected = {'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'number': '123',
          'price': '44.95',
          'specificvalue': '123',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2000-11-17',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'number': '123',
          'price': '5.95',
          'specificvalue': '123',
          'publish_date': '2001-09-10',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'number': '123',
          'price': '4.95',
          'specificvalue': '123',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'number': '123',
          'price': '4.95',
          'specificvalue': '123',
          'publish_date': '2000-11-02',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'number': '123',
          'price': '4.95',
          'specificvalue': '123',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'number': '123',
          'price': '6.95',
          'specificvalue': '123',
          'publish_date': '2000-11-02',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'number': '123',
          'price': '36.95',
          'specificvalue': '123',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'number': '123',
          'price': '36.95',
          'specificvalue': '123',
          'publish_date': '2000-12-01',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'number': '123',
          'price': '49.95',
          'specificvalue': '123',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}],
   '2': [{'author': 'Gambardella, Matthew',
          'number': '123',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'number': '123',
          'price': '5.95',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'number': '123',
          'price': '4.95',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'number': '123',
          'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'number': '123',
          'price': '4.95',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'number': '123',
          'price': '6.95',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'number': '123',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_optional_external_data_start(self):

        profile = """catalog
        lowest
            number = external_dataset:__external_value__1
            book
                __NEW_EXTERNAL_VALUE_HOLDER__ = __external_value__1:externaldata
                optionalexternalstart
                    externaldata = external_dataset:__external_value__1
                id     = dataset:1
                author = dataset:1 dataset:2
                title  = dataset:1 dataset:2
                genre  = dataset:1
                price  = dataset:1 dataset:2
                publish_date = dataset:1
                description  = dataset:1
                __EXTERNAL_VALUE__ = __external_value__1:number:1 __external_value__1:number:2 __external_value__1:externaldata:1"""

        expected = {'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'number': '123',
          'price': '44.95',
          'externaldata': 'external_value1',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'number': '123',
          'price': '5.95',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'number': '123',
          'price': '5.95',
          'publish_date': '2000-11-17',
          'externaldata': 'external_value2',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'number': '123',
          'price': '5.95',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'number': '123',
          'price': '5.95',
          'publish_date': '2001-09-10',
          'externaldata': 'external_value3',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-11-02',
          'externaldata': 'external_value4',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'number': '123',
          'price': '6.95',
          'publish_date': '2000-11-02',
          'externaldata': 'external_value5',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'number': '123',
          'price': '36.95',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'number': '123',
          'price': '36.95',
          'publish_date': '2000-12-01',
          'externaldata': 'external_value6',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'number': '123',
          'price': '49.95',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}],
   '2': [{'author': 'Gambardella, Matthew',
          'number': '123',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'number': '123',
          'price': '5.95',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'number': '123',
          'price': '4.95',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'number': '123',
          'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'number': '123',
          'price': '4.95',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'number': '123',
          'price': '6.95',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'number': '123',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_optional_external_data_end(self):

        profile = """catalog
        lowest
            number = external_dataset:__external_value__1
            book
                __NEW_EXTERNAL_VALUE_HOLDER__ = __external_value__1:externaldata
                optionalexternalend
                    externaldata = external_dataset:__external_value__1
                id     = dataset:1
                author = dataset:1 dataset:2
                title  = dataset:1 dataset:2
                genre  = dataset:1
                price  = dataset:1 dataset:2
                publish_date = dataset:1
                description  = dataset:1
                __EXTERNAL_VALUE__ = __external_value__1:number:1 __external_value__1:number:2 __external_value__1:externaldata:1"""

        expected = {'1': [{'author': 'Gambardella, Matthew',
          'description': 'An in-depth look at creating applications\n         with XML.',
          'genre': 'Computer',
          'id': 'bk101',
          'number': '123',
          'price': '44.95',
          'externaldata': 'external_value1',
          'publish_date': '2000-10-01',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
          'genre': 'Fantasy',
          'id': 'bk102',
          'number': '123',
          'price': '5.95',
          'publish_date': '2000-12-16',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
          'genre': 'Fantasy',
          'id': 'bk103',
          'number': '123',
          'price': '5.95',
          'publish_date': '2000-11-17',
          'externaldata': 'external_value2',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
          'genre': 'Fantasy',
          'id': 'bk104',
          'number': '123',
          'price': '5.95',
          'publish_date': '2001-03-10',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
          'genre': 'Fantasy',
          'id': 'bk105',
          'number': '123',
          'price': '5.95',
          'publish_date': '2001-09-10',
          'externaldata': 'external_value3',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
          'genre': 'Romance',
          'id': 'bk106',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-09-02',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
          'genre': 'Romance',
          'id': 'bk107',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-11-02',
          'externaldata': 'external_value4',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
          'genre': 'Horror',
          'id': 'bk108',
          'number': '123',
          'price': '4.95',
          'publish_date': '2000-12-06',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
          'genre': 'Science Fiction',
          'id': 'bk109',
          'number': '123',
          'price': '6.95',
          'publish_date': '2000-11-02',
          'externaldata': 'external_value5',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
          'genre': 'Computer',
          'id': 'bk110',
          'number': '123',
          'price': '36.95',
          'publish_date': '2000-12-09',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
          'genre': 'Computer',
          'id': 'bk111',
          'number': '123',
          'price': '36.95',
          'publish_date': '2000-12-01',
          'externaldata': 'external_value6',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
          'genre': 'Computer',
          'id': 'bk112',
          'number': '123',
          'price': '49.95',
          'publish_date': '2001-04-16',
          'title': 'Visual Studio 7: A Comprehensive Guide'}],
   '2': [{'author': 'Gambardella, Matthew',
          'number': '123',
          'price': '44.95',
          'title': "XML Developer's Guide"},
         {'author': 'Ralls, Kim',
          'number': '123',
          'price': '5.95',
          'title': 'Midnight Rain'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'Maeve Ascendant'},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': "Oberon's Legacy"},
         {'author': 'Corets, Eva',
          'number': '123',
          'price': '5.95',
          'title': 'The Sundered Grail'},
         {'author': 'Randall, Cynthia',
          'number': '123',
          'price': '4.95',
          'title': 'Lover Birds'},
         {'author': 'Thurman, Paula',
          'number': '123',
          'price': '4.95',
          'title': 'Splish Splash'},
         {'author': 'Knorr, Stefan',
          'number': '123',
          'price': '4.95',
          'title': 'Creepy Crawlies'},
         {'author': 'Kress, Peter',
          'number': '123',
          'price': '6.95',
          'title': 'Paradox Lost'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'Microsoft .NET: The Programming Bible'},
         {'author': "O'Brien, Tim",
          'number': '123',
          'price': '36.95',
          'title': 'MSXML3: A Comprehensive Guide'},
         {'author': 'Galos, Mike',
          'number': '123',
          'price': '49.95',
          'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_default_dataset(self):

        profile = """catalog
        lowest
                book
                        missing = dataset:1,default:
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'missing': '',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'missing': '',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'missing': '',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'missing': '',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'missing': '',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'missing': '',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'missing': '',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'missing': '',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'missing': '',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'missing': '',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'missing': '',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'missing': '',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_default_nested_dataset(self):

        profile = """catalog
        lowest
                book
                        missing = dataset:1,default:
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1
                        __ALWAYS_FOLLOW__ = nested_level1
                        nested_level1
                           missing_data1 = dataset:1,default:
                           __ALWAYS_FOLLOW__ = nested_level2
                           nested_level2
                              missing_data2 = dataset:1,default:
                              __ALWAYS_FOLLOW__ = nested_level3
                              nested_level3
                                 missing_data3 = dataset:1,default:"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'missing': '',
                 'missing_data1': '',
                 'missing_data2': '',
                 'missing_data3': '',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        try:
           output = parse_using_profile(self.xml, profile)
        except Exception as e:
            print(e)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    def test_default_dataset_non_null(self):

        profile = """catalog
        lowest
                book
                        missing = dataset:1,default:xyz
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'missing': 'xyz',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'missing': 'xyz',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'missing': 'xyz',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'missing': 'xyz',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'missing': 'xyz',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'missing': 'xyz',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'missing': 'xyz',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'missing': 'xyz',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'missing': 'xyz',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'missing': 'xyz',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'missing': 'xyz',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'missing': 'xyz',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile)
        self.maxDiff = None
        self.assertDictEqual(expected, output)

    #def setUp(self):
    def test_xmldataset_object_creation(self):
        """ doctype comments """
        from xmldataset import _XMLDataset
        object = _XMLDataset({})
        pass

    def test_global_values(self):

        profile = """catalog
        lowest
                book
                        id     = dataset:1
                        author = dataset:1
                        title  = dataset:1
                        genre  = dataset:1
                        price  = dataset:1
                        publish_date = dataset:1
                        description  = dataset:1"""

        expected = {   '1': [   {   'author': 'Gambardella, Matthew',
                 'description': 'An in-depth look at creating applications\n         with XML.',
                 'genre': 'Computer',
                 'id': 'bk101',
                 'location': 'Chorleywood',
                 'price': '44.95',
                 'publish_date': '2000-10-01',
                 'title': "XML Developer's Guide"},
             {   'author': 'Ralls, Kim',
                 'description': 'A former architect battles corporate zombies,\n         an evil sorceress, and her own childhood to become queen\n         of the world.',
                 'genre': 'Fantasy',
                 'id': 'bk102',
                 'location': 'Chorleywood',
                 'price': '5.95',
                 'publish_date': '2000-12-16',
                 'title': 'Midnight Rain'},
             {   'author': 'Corets, Eva',
                 'description': 'After the collapse of a nanotechnology\n         society in England, the young survivors lay the\n         foundation for a new society.',
                 'genre': 'Fantasy',
                 'id': 'bk103',
                 'location': 'Chorleywood',
                 'price': '5.95',
                 'publish_date': '2000-11-17',
                 'title': 'Maeve Ascendant'},
             {   'author': 'Corets, Eva',
                 'description': 'In post-apocalypse England, the mysterious\n         agent known only as Oberon helps to create a new life\n         for the inhabitants of London. Sequel to Maeve\n         Ascendant.',
                 'genre': 'Fantasy',
                 'id': 'bk104',
                 'location': 'Chorleywood',
                 'price': '5.95',
                 'publish_date': '2001-03-10',
                 'title': "Oberon's Legacy"},
             {   'author': 'Corets, Eva',
                 'description': "The two daughters of Maeve, half-sisters,\n         battle one another for control of England. Sequel to\n         Oberon's Legacy.",
                 'genre': 'Fantasy',
                 'id': 'bk105',
                 'location': 'Chorleywood',
                 'price': '5.95',
                 'publish_date': '2001-09-10',
                 'title': 'The Sundered Grail'},
             {   'author': 'Randall, Cynthia',
                 'description': 'When Carla meets Paul at an ornithology\n         conference, tempers fly as feathers get ruffled.',
                 'genre': 'Romance',
                 'id': 'bk106',
                 'location': 'Chorleywood',
                 'price': '4.95',
                 'publish_date': '2000-09-02',
                 'title': 'Lover Birds'},
             {   'author': 'Thurman, Paula',
                 'description': 'A deep sea diver finds true love twenty\n         thousand leagues beneath the sea.',
                 'genre': 'Romance',
                 'id': 'bk107',
                 'location': 'Chorleywood',
                 'price': '4.95',
                 'publish_date': '2000-11-02',
                 'title': 'Splish Splash'},
             {   'author': 'Knorr, Stefan',
                 'description': 'An anthology of horror stories about roaches,\n         centipedes, scorpions  and other insects.',
                 'genre': 'Horror',
                 'id': 'bk108',
                 'location': 'Chorleywood',
                 'price': '4.95',
                 'publish_date': '2000-12-06',
                 'title': 'Creepy Crawlies'},
             {   'author': 'Kress, Peter',
                 'description': 'After an inadvertant trip through a Heisenberg\n         Uncertainty Device, James Salway discovers the problems\n         of being quantum.',
                 'genre': 'Science Fiction',
                 'id': 'bk109',
                 'location': 'Chorleywood',
                 'price': '6.95',
                 'publish_date': '2000-11-02',
                 'title': 'Paradox Lost'},
             {   'author': "O'Brien, Tim",
                 'description': "Microsoft's .NET initiative is explored in\n         detail in this deep programmer's reference.",
                 'genre': 'Computer',
                 'id': 'bk110',
                 'location': 'Chorleywood',
                 'price': '36.95',
                 'publish_date': '2000-12-09',
                 'title': 'Microsoft .NET: The Programming Bible'},
             {   'author': "O'Brien, Tim",
                 'description': 'The Microsoft MSXML3 parser is covered in\n         detail, with attention to XML DOM interfaces, XSLT processing,\n         SAX and more.',
                 'genre': 'Computer',
                 'id': 'bk111',
                 'location': 'Chorleywood',
                 'price': '36.95',
                 'publish_date': '2000-12-01',
                 'title': 'MSXML3: A Comprehensive Guide'},
             {   'author': 'Galos, Mike',
                 'description': 'Microsoft Visual Studio 7 is explored in depth,\n         looking at how Visual Basic, Visual C++, C#, and ASP+ are\n         integrated into a comprehensive development\n         environment.',
                 'genre': 'Computer',
                 'id': 'bk112',
                 'location': 'Chorleywood',
                 'price': '49.95',
                 'publish_date': '2001-04-16',
                 'title': 'Visual Studio 7: A Comprehensive Guide'}]}

        output = parse_using_profile(self.xml, profile, global_values = {'location' : 'Chorleywood'})
        self.maxDiff = None
        self.assertDictEqual(expected, output)


if __name__ == '__main__':

    unittest.main()
