import xmldataset
import pprint

# Setup Pretty Printing
ppsetup = pprint.PrettyPrinter(indent=4)
pp = ppsetup.pprint

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

profile="""
catalog
    shop
        book
            id     = dataset:title_and_author dataset:title_and_genre
            author = dataset:title_and_author
            title  = dataset:title_and_author dataset:title_and_genre
            genre  = dataset:title_and_genre"""

# Pretty Print the output
output = xmldataset.parse_using_profile(xml,profile)
pp(output)
