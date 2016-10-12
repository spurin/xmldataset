from xmldataset import parse_using_profile
import pprint

# ------------------------------------------------------------------------------
#    Define Profile
# ------------------------------------------------------------------------------
profile = """
catalog
    lowest
        book
            author = dataset:title_and_author
            title  = dataset:title_and_author
            missing  = dataset:title_and_author
"""

# ------------------------------------------------------------------------------
#    Define XML
# ------------------------------------------------------------------------------
xml = """<?xml version="1.0"?>
<catalog>
   <lowest number="123">
      <specificbefore>
         <specificvalue>123</specificvalue>
      </specificbefore>
      <book id="bk101">
         <optionalexternal>
            <externaldata>external_value1</externaldata>
         </optionalexternal>
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
      <book id="bk103">
         <optionalexternal>
            <externaldata>external_value2</externaldata>
         </optionalexternal>
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
      <book id="bk105">
         <optionalexternal>
            <externaldata>external_value3</externaldata>
         </optionalexternal>
         <author>Corets, Eva</author>
         <title>The Sundered Grail</title>
         <genre>Fantasy</genre>
         <price>5.95</price>
         <publish_date>2001-09-10</publish_date>
         <description>The two daughters of Maeve, half-sisters,
         battle one another for control of England. Sequel to
         Oberon's Legacy.</description>
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
         <optionalexternal>
            <externaldata>external_value4</externaldata>
         </optionalexternal>
         <author>Thurman, Paula</author>
         <title>Splish Splash</title>
         <genre>Romance</genre>
         <price>4.95</price>
         <publish_date>2000-11-02</publish_date>
         <description>A deep sea diver finds true love twenty
         thousand leagues beneath the sea.</description>
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
         <optionalexternal>
            <externaldata>external_value5</externaldata>
         </optionalexternal>
         <author>Kress, Peter</author>
         <title>Paradox Lost</title>
         <genre>Science Fiction</genre>
         <price>6.95</price>
         <publish_date>2000-11-02</publish_date>
         <description>After an inadvertant trip through a Heisenberg
         Uncertainty Device, James Salway discovers the problems
         of being quantum.</description>
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
         <optionalexternal>
            <externaldata>external_value6</externaldata>
         </optionalexternal>
         <author>O'Brien, Tim</author>
         <title>MSXML3: A Comprehensive Guide</title>
         <genre>Computer</genre>
         <price>36.95</price>
         <publish_date>2000-12-01</publish_date>
         <description>The Microsoft MSXML3 parser is covered in
         detail, with attention to XML DOM interfaces, XSLT processing,
         SAX and more.</description>
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
      <specificafter>
         <specificvalue>123</specificvalue>
      </specificafter>
   </lowest>
</catalog>"""

# ------------------------------------------------------------------------------
#    Setup Pretty Printing
# ------------------------------------------------------------------------------
ppsetup = pprint.PrettyPrinter(indent=4)
pp = ppsetup.pprint

# ------------------------------------------------------------------------------
#    Call parse_using_profile
# ------------------------------------------------------------------------------
print(parse_using_profile(xml, profile))
