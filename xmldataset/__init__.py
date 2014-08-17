""" Extracts XML into Python Datasets based upon a simple text profile markup language """

# -*- coding: utf-8 -*-
#  pylint: disable=line-too-long

__author__ = 'James Spurin'
__email__ = 'james@spurin.com'
__version__ = '0.1.1'

import re
import logging

#-------------------------------------------------------------------------------
#   Attempt to use cElementTree, otherwise fall back on ElementTree
#-------------------------------------------------------------------------------
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#-------------------------------------------------------------------------------
#   class _XMLDataset
#-------------------------------------------------------------------------------
class _XMLDataset(): # pylint: disable=R0902,R0903
    """Internal class used as parsing handler"""

    def __init__(self, options):
        """Object initialisation"""

        #-------------------------------------------------------------------------------
        #   Store supplied options in object
        #-------------------------------------------------------------------------------
        self.__dict__ = options

        #-------------------------------------------------------------------------------
        #   Create an internal logging object
        #-------------------------------------------------------------------------------
        self.logger = logging.getLogger('default')
        self.logger.setLevel(logging.DEBUG)

        #-------------------------------------------------------------------------------
        #   Set the depth as 0, used to track the depth of the XML position
        #-------------------------------------------------------------------------------
        self._depth = 0

        #-------------------------------------------------------------------------------
        #   Store for Profiles
        #-------------------------------------------------------------------------------
        self._profiles = []

        #-------------------------------------------------------------------------------
        #   Store for Current Data
        #-------------------------------------------------------------------------------
        self.current_data = {}

        #-------------------------------------------------------------------------------
        #   Store for Data Structure
        #-------------------------------------------------------------------------------
        self.data_structure = {}

        #-------------------------------------------------------------------------------
        #   Store for External Data
        #-------------------------------------------------------------------------------
        self.external_data = {}

    def _expand_profile(self, profile_input):
        """Expands the supplied profile to a python data structure"""

        #-------------------------------------------------------------------------------
        #   Declare the Indentation History as starting at 0
        #-------------------------------------------------------------------------------
        indentation_history = [0]

        #-------------------------------------------------------------------------------
        #   Profile holders
        #-------------------------------------------------------------------------------
        complex_profile = {}
        complex_profile_history = [complex_profile]
        current_profile_position = complex_profile_history[-1]

        #-------------------------------------------------------------------------------
        #   Capture available tokens from the profile input using a carriage return
        #   as a separator
        #-------------------------------------------------------------------------------
        tokens = profile_input.split('\n')

        #-------------------------------------------------------------------------------
        #   Process each token
        #-------------------------------------------------------------------------------
        for token in tokens:

            #-------------------------------------------------------------------------------
            #   Declare holders for the length_indentation and token_data
            #-------------------------------------------------------------------------------
            length_indentation = None
            token_data = None

            #-------------------------------------------------------------------------------
            #   Attempt to match token with indentation
            #-------------------------------------------------------------------------------
            match = re.search('(\s+)(.*)', token) # pylint: disable=W1401

            #-------------------------------------------------------------------------------
            #   If a match is found capture the indentation and the token_data
            #-------------------------------------------------------------------------------
            if match:
                length_indentation = len(match.group(1))
                token_data = match.group(2).strip()
            #-------------------------------------------------------------------------------
            #   Otherwise mark the indentation as 0 and remove any carriage returns from
            #   the token_data
            #-------------------------------------------------------------------------------
            else:
                length_indentation = 0
                token_data = token.strip()

            #-------------------------------------------------------------------------------
            #   If token data is available
            #-------------------------------------------------------------------------------
            if token_data:

                #-------------------------------------------------------------------------------
                #   Store the previous_indentation information
                #-------------------------------------------------------------------------------
                previous_indentation = indentation_history[-1]

                #-------------------------------------------------------------------------------
                #    If the indentation has increased, store the indentation in the history
                #-------------------------------------------------------------------------------
                if length_indentation > previous_indentation:
                    indentation_history.append(length_indentation)

                #-------------------------------------------------------------------------------
                #    Otherwise if the indentation has decreased
                #-------------------------------------------------------------------------------
                elif previous_indentation > length_indentation:

                    #-------------------------------------------------------------------------------
                    #    Step back through the indentation
                    #-------------------------------------------------------------------------------
                    while previous_indentation > length_indentation:
                        indentation_history.pop()
                        previous_indentation = indentation_history[-1]

                        #-------------------------------------------------------------------------------
                        #    ... And the associated history
                        #-------------------------------------------------------------------------------
                        complex_profile_history.pop()
                        current_profile_position = complex_profile_history[-1]

                #-------------------------------------------------------------------------------
                #    If the token contains a value ( signified by an = sign )
                #-------------------------------------------------------------------------------
                if '=' in token_data:

                    #-------------------------------------------------------------------------------
                    #    Capture the key and the record_holder
                    #-------------------------------------------------------------------------------
                    key, record_holder = token_data.split('=')

                    #-------------------------------------------------------------------------------
                    #    Remove leading and ending space using strip() for the key and record_holder
                    #-------------------------------------------------------------------------------
                    key = key.strip()
                    record_holder = record_holder.strip()

                    #-------------------------------------------------------------------------------
                    #    Check for an Ignore marker
                    #-------------------------------------------------------------------------------
                    if record_holder == '__IGNORE__':

                        if key not in current_profile_position:
                            current_profile_position[key] = {}

                        current_profile_position[key]['__IGNORE__'] = 1
                    
                    #-------------------------------------------------------------------------------
                    #    Otherwise continue
                    #-------------------------------------------------------------------------------
                    else:

                        #-------------------------------------------------------------------------------
                        #    Split unprocessed records
                        #-------------------------------------------------------------------------------
                        records_unprocessed = record_holder.split(' ')

                        #-------------------------------------------------------------------------------
                        #    Capture New Dataset markers where available
                        #-------------------------------------------------------------------------------
                        if key == '__NEW_DATASET__':
                            current_profile_position['__NEW_DATASET__'] = records_unprocessed

                        #-------------------------------------------------------------------------------
                        #    Otherwise Capture External Values where available
                        #-------------------------------------------------------------------------------
                        elif key == '__EXTERNAL_VALUE__':
                            current_profile_position['__EXTERNAL_VALUE__'] = records_unprocessed

                        #-------------------------------------------------------------------------------
                        #    Otherwise Capture External Values where available
                        #-------------------------------------------------------------------------------
                        elif key == '__NEW_EXTERNAL_VALUE_HOLDER__':
                            current_profile_position['__NEW_EXTERNAL_VALUE_HOLDER__'] = records_unprocessed

                        #-------------------------------------------------------------------------------
                        #    Otherwise ....
                        #-------------------------------------------------------------------------------
                        else:

                            #-------------------------------------------------------------------------------
                            #    Add an order processing sequence to the profile, create where necessary
                            #    or append
                            #-------------------------------------------------------------------------------
                            if '__order__' not in current_profile_position:
                                current_profile_position['__order__'] = [key]
                            else:
                                current_profile_position['__order__'].append(key)

                            #-------------------------------------------------------------------------------
                            #    Process records_unprocessed
                            #-------------------------------------------------------------------------------
                            for record_unprocessed in records_unprocessed:

                                #-------------------------------------------------------------------------------
                                #    Add the key
                                #-------------------------------------------------------------------------------
                                if key not in current_profile_position:
                                    current_profile_position[key] = {}

                                #-------------------------------------------------------------------------------
                                #    Create the record holder or append a new record
                                #-------------------------------------------------------------------------------
                                if '__record__' not in current_profile_position[key]:
                                    current_profile_position[key]['__record__'] = [{}]
                                else:
                                    current_profile_position[key]['__record__'].append({})

                                #-------------------------------------------------------------------------------
                                #    Process each record
                                #-------------------------------------------------------------------------------
                                for record in record_unprocessed.split(','):
                                    record_key, record_value = record.split(':')
                                    current_profile_position[key]['__record__'][-1][record_key] = record_value

                #-------------------------------------------------------------------------------
                #    If the token does not contain an = sign
                #-------------------------------------------------------------------------------
                else:

                    #-------------------------------------------------------------------------------
                    #    Create a named dictionary
                    #-------------------------------------------------------------------------------
                    holder = {}

                    #-------------------------------------------------------------------------------
                    #    Store the named dictionary as the current token
                    #-------------------------------------------------------------------------------
                    current_profile_position[token_data] = holder

                    #-------------------------------------------------------------------------------
                    #    Add an order processing sequence
                    #-------------------------------------------------------------------------------
                    if '__order__' not in current_profile_position:
                        current_profile_position['__order__'] = [token_data]
                    else:
                        current_profile_position['__order__'].append(token_data)

                    #-------------------------------------------------------------------------------
                    #    Update the current position to the named dict
                    #-------------------------------------------------------------------------------
                    current_profile_position = holder

                    #-------------------------------------------------------------------------------
                    #    Add to the current history
                    #-------------------------------------------------------------------------------
                    complex_profile_history.append(holder)

        #-------------------------------------------------------------------------------
        #    Return the complex profile
        #-------------------------------------------------------------------------------
        return complex_profile

    def _process_record(self, record, name, value):
        """Logic for processing each record"""

        #-------------------------------------------------------------------------------
        #    If a custom name has been provided use accordingly, otherwise use name
        #-------------------------------------------------------------------------------
        name = record['name'] if 'name' in record else name

        #-------------------------------------------------------------------------------
        #    If a prefix has been provided use accordingly
        #-------------------------------------------------------------------------------
        name = record['prefix'] + name if 'prefix' in record else name
        
        #-------------------------------------------------------------------------------
        #    If a process handler has been specified call accordingly
        #-------------------------------------------------------------------------------
        if 'process' in record:
            
            # Capture the coderef from the object
            coderef = None

            if hasattr(self, 'process'):
                if record['process'] in self.process:
                    value = self.process[record['process']](value)
                else:
                   raise Exception('process coderef ' + record['process'] + ' missing')
            else:
                raise Exception('process definition not supplied as argument')

        #-------------------------------------------------------------------------------
        #    If the record contains a dataset
        #-------------------------------------------------------------------------------
        if 'dataset' in record:

            #-------------------------------------------------------------------------------
            #    Check if the current dataset doesn't exist or if the key in question already exists
            #    If so, create a new data_structure holder
            #-------------------------------------------------------------------------------
            if not record['dataset'] in self.data_structure or name in self.data_structure[record['dataset']][-1]:

                #-------------------------------------------------------------------------------
                #    Dispatch existing data
                #-------------------------------------------------------------------------------
                self._dispatch_dataset(record['dataset'])

                #-------------------------------------------------------------------------------
                #    If the current dataset does not exist in the data structure add 
                #    a new entry holder
                #-------------------------------------------------------------------------------
                if record['dataset'] not in self.data_structure:
                    self.data_structure[record['dataset']] = [{}]
                else:
                    self.data_structure[record['dataset']].append({})
                
            #-------------------------------------------------------------------------------
            #    Add the value to the holder
            #-------------------------------------------------------------------------------
            self.data_structure[record['dataset']][-1][name] = value

        #-------------------------------------------------------------------------------
        #    If the record contains an external_dataset
        #-------------------------------------------------------------------------------
        if 'external_dataset' in record:

            #-------------------------------------------------------------------------------
            #    If the external dataset doesn't exist in the data structure add accordingly
            #-------------------------------------------------------------------------------
            if record['external_dataset'] not in self.external_data:
                self.external_data[record['external_dataset']] = {}

            #-------------------------------------------------------------------------------
            #    If the holder doesn't exist, add accordingly, add a default value of ''
            #-------------------------------------------------------------------------------
            if name not in self.external_data[record['external_dataset']]:
                self.external_data[record['external_dataset']][name] = ['']

            #-------------------------------------------------------------------------------
            #    Store the data, if the last entry equals '', update otherwise append as
            #    a new value
            #-------------------------------------------------------------------------------
            if self.external_data[record['external_dataset']][name][-1] == '':
                self.external_data[record['external_dataset']][name][-1] = value
            else:
                self.external_data[record['external_dataset']][name].append(value)

    def _dispatch_all(self):
        """Dispatch all datasets"""

        if hasattr(self, 'dispatch'):
            dataset_list = []

            #-------------------------------------------------------------------------------
            #    Make a list of dataset keys without referencing the original values
            #-------------------------------------------------------------------------------
            for dataset in self.data_structure.keys():
                dataset_list.append(str(dataset))
                
            #-------------------------------------------------------------------------------
            #    Dispatch each dataset.  This approach of separately capturing keys prior to
            #    processing was taken as the iterator complains about the list changing 
            #    during processing ( owing to the del method used in _dispatch_dataset )
            #-------------------------------------------------------------------------------
            for dataset in dataset_list:
                self._dispatch_dataset(dataset, flush=1)
    
    def _dispatch_dataset(self, dataset, flush=0):
        """Dispatch datasets"""
        
        #-------------------------------------------------------------------------------
        #    Set a default trigger and code holder
        #-------------------------------------------------------------------------------
        counter_trigger = 0
        counter_coderef = None
        
        #-------------------------------------------------------------------------------
        #    If the object contains dispatch logic
        #-------------------------------------------------------------------------------
        if hasattr(self, 'dispatch'):
            
            #-------------------------------------------------------------------------------
            #    Check for dataset specific dispatch
            #-------------------------------------------------------------------------------
            if dataset in self.dispatch:
                if 'counter' in self.dispatch[dataset]:
                    counter_trigger = self.dispatch[dataset]['counter']
            
            #-------------------------------------------------------------------------------
            #    Check for a generic dispatch counter
            #-------------------------------------------------------------------------------
            elif '__generic__' in self.dispatch:
                if 'counter' in self.dispatch['__generic__']:
                    counter_trigger = self.dispatch['__generic__']['counter']

            #-------------------------------------------------------------------------------
            #    Check for dataset specific code
            #-------------------------------------------------------------------------------
            if dataset in self.dispatch:
                if 'coderef' in self.dispatch[dataset]:
                    counter_coderef = self.dispatch[dataset]['coderef']
            
            #-------------------------------------------------------------------------------
            #    Check for a generic dispatch code
            #-------------------------------------------------------------------------------
            elif '__generic__' in self.dispatch:
                if 'coderef' in self.dispatch['__generic__']:
                    counter_coderef = self.dispatch['__generic__']['coderef']
            
            #-------------------------------------------------------------------------------
            #    If we have enough records, dispatch accordingly
            #-------------------------------------------------------------------------------
            if dataset in self.data_structure:
                if len(self.data_structure[dataset]) >= counter_trigger or flush:
                
                    # Call the coderef with the payload, send as dict with dataset value
                    counter_coderef( { dataset : self.data_structure[dataset] })
                
                    # Delete the datastructure
                    del self.data_structure[dataset]
                    
    def _process_data(self, xml_root):
        """Process data"""

        def process_element():
            """ Docstring holder """

            #-------------------------------------------------------------------------------
            #    Store the previous element if applicable
            #-------------------------------------------------------------------------------
            self._previous_key = self._current_key if hasattr(self, '_current_key') else ''

            #-------------------------------------------------------------------------------
            #    Store the current element name
            #-------------------------------------------------------------------------------
            self._current_key = xml_root.tag

            #-------------------------------------------------------------------------------
            #    Move to the appropriate profile for the correct depth
            #-------------------------------------------------------------------------------
            while self._profiles and len(self._profiles) > self._depth:
                self._profile = self._profiles.pop()

            #-------------------------------------------------------------------------------
            #    Check if the key is in the profile
            #-------------------------------------------------------------------------------
            if self._current_key in self._profile:

                #-------------------------------------------------------------------------------
                #    Store the old profile
                #-------------------------------------------------------------------------------
                self._profiles.append(self._profile)
                
                #-------------------------------------------------------------------------------
                #    Update the profile to the current key
                #-------------------------------------------------------------------------------
                self._profile = self._profile[self._current_key]

                #-------------------------------------------------------------------------------
                #    Skip if __IGNORE__
                #-------------------------------------------------------------------------------
                if '__IGNORE__' in self._profile:
                    next

                #-------------------------------------------------------------------------------
                #    Otherwise continue
                #-------------------------------------------------------------------------------
                else:

                    #-------------------------------------------------------------------------------
                    #    If an external value has been specified
                    #-------------------------------------------------------------------------------
                    if '__NEW_EXTERNAL_VALUE_HOLDER__' in self._profile:
                        for dataset in self._profile['__NEW_EXTERNAL_VALUE_HOLDER__']:

                            # Holder for __EXTERNAL_REFERENCES__
                            values = dataset.split(':')
                            ext_dataset = values[0]
                            ext_name = values[1]

                            # Delete the existing value
                            if ext_dataset in self.external_data:
                                    if ext_name in self.external_data[ext_dataset]:
                                        del self.external_data[ext_dataset][ext_name]
                                        #self.external_data[ext_dataset][ext_name].append('')

                    #-------------------------------------------------------------------------------
                    #    If a new dataset has been specified
                    #-------------------------------------------------------------------------------
                    if '__NEW_DATASET__' in self._profile:
                        for dataset in self._profile['__NEW_DATASET__']:
                                
                            #-------------------------------------------------------------------------------
                            #    Dispatch existing datasets
                            #-------------------------------------------------------------------------------
                            self._dispatch_dataset(dataset)

                            #-------------------------------------------------------------------------------
                            #    Create the dataset if it doesn't already exist
                            #-------------------------------------------------------------------------------
                            if dataset not in self.data_structure:
                                self.data_structure[dataset] = [{}]
                            else:
                                self.data_structure[dataset].append({})

                    #-------------------------------------------------------------------------------
                    #    Process records where available, i.e. found in the same layer
                    #-------------------------------------------------------------------------------
                    if '__record__' in self._profile:

                        #-------------------------------------------------------------------------------
                        #    Process each record
                        #-------------------------------------------------------------------------------
                        for record in self._profile['__record__']:
                            self._process_record(record, xml_root.tag, xml_root.text)
                            
                    #-------------------------------------------------------------------------------
                    #    Walk path based on order
                    #-------------------------------------------------------------------------------
                    if '__order__' in self._profile:
                        for order_value in self._profile['__order__']:

                            #-------------------------------------------------------------------------------
                            #    Match Marker
                            #-------------------------------------------------------------------------------
                            match = 0
                           
                            #-------------------------------------------------------------------------------
                            #    Check attributes against order_value
                            #-------------------------------------------------------------------------------
                            if order_value in xml_root.attrib:
                                match = 1

                                #-------------------------------------------------------------------------------
                                #    If the attribute has a profile entry, process each record
                                #-------------------------------------------------------------------------------
                                if order_value in self._profile:
                                    if '__record__' in self._profile[order_value]:

                                        # Process each record
                                        for record in self._profile[order_value]['__record__']:
                                            self._process_record(record, order_value, xml_root.attrib[order_value])

                            #-------------------------------------------------------------------------------
                            #    List all available elements and look for a match against order_value
                            #-------------------------------------------------------------------------------
                            for element in xml_root:
                                if order_value == element.tag:
                                    match = 1
                                    
                                    #-------------------------------------------------------------------------------
                                    #    Increase the depth as we follow
                                    #-------------------------------------------------------------------------------
                                    self._depth += 1

                                    #-------------------------------------------------------------------------------
                                    #    Follow Element
                                    #-------------------------------------------------------------------------------
                                    self._process_data(element)

                                    #-------------------------------------------------------------------------------
                                    #    Decrease the depth as we exit
                                    #-------------------------------------------------------------------------------
                                    self._depth -= 1

                                    # Pop the last profile
                                    self._profile = self._profiles.pop()
                                    
                            #-------------------------------------------------------------------------------
                            #    If there is not a match
                            #-------------------------------------------------------------------------------
                            if not match:
                                # Future functionality
                                pass

                    #-------------------------------------------------------------------------------
                    #    If an external value has been specified
                    #-------------------------------------------------------------------------------
                    if '__EXTERNAL_VALUE__' in self._profile:
                        for dataset in self._profile['__EXTERNAL_VALUE__']:

                            # Holder for __EXTERNAL_REFERENCES__
                            values = dataset.split(':')
                            ext_dataset = values[0]
                            ext_name = values[1]
                            forward_dataset = values[2]
                            forward_name = values[3] if len(values) > 3 else ext_name
                            
                            #-------------------------------------------------------------------------------
                            #    Create a new dataset holder if one doesn't exist
                            #-------------------------------------------------------------------------------
                            if forward_dataset not in self.data_structure:
                                self.data_structure[forward_dataset] = [{}]

                            #-------------------------------------------------------------------------------
                            #    Otherwise if the value already exists
                            #-------------------------------------------------------------------------------
                            elif forward_name in self.data_structure[forward_dataset][-1]:

                                #-------------------------------------------------------------------------------
                                #    Dispatch dataset where applicable
                                #-------------------------------------------------------------------------------
                                self._dispatch_dataset(forward_dataset)

                                #-------------------------------------------------------------------------------
                                #    Recreate the holder or add a new position ( dependant on whether or not
                                #    the data was dispatched as per the object dispatch attribute
                                #-------------------------------------------------------------------------------
                                if forward_dataset not in self.data_structure:
                                    self.data_structure[forward_dataset] = [{}]
                                else:
                                    self.data_structure[forward_dataset].append({})

                            #-------------------------------------------------------------------------------
                            #    Verify that the external data does not already exist within the dataset,
                            #    If it doesn't store accordingly
                            #-------------------------------------------------------------------------------
                            if ext_dataset not in self.external_data:
                                self.external_data[ext_dataset] = {}
                            if ext_name not in self.external_data[ext_dataset]:
                                self.external_data[ext_dataset][ext_name] = ['']
                            else:
                                #-------------------------------------------------------------------------------
                                #    Update the Alias
                                #-------------------------------------------------------------------------------
                                self.data_structure[forward_dataset][-1][forward_name] = self.external_data[ext_dataset][ext_name][-1]

        #-------------------------------------------------------------------------------
        #    Type Lookup Dictionary to Code
        #-------------------------------------------------------------------------------
        tokenDict = {
         "<class 'xml.etree.ElementTree.Element'>" : process_element,
         "<class 'xml.etree.ElementTree._ElementInterface'>" : process_element,
         "<class 'Element'>" : process_element,
         "<type 'Element'>"  : process_element,
         "<type 'instance'>" : process_element,
        }

        #-------------------------------------------------------------------------------
        #    Dispatch accordingly based on the type
        #-------------------------------------------------------------------------------
        tokenDict[str(type(xml_root))]()

def parse_using_profile(xml, profile, **options):
    """Parses XML based upon the profile"""
    
    #-------------------------------------------------------------------------------
    #    Create an object, passing the options to the object
    #-------------------------------------------------------------------------------
    obj = _XMLDataset(options)

    #-------------------------------------------------------------------------------
    #    Convert the source input profile to a python structure
    #-------------------------------------------------------------------------------
    obj._profile = obj._expand_profile(profile)    

    #-------------------------------------------------------------------------------
    #    Capture an ElementTree.Element from an XML String ( Equivalent to 
    #    getroot() on parse file )
    #-------------------------------------------------------------------------------
    xml_root = ET.fromstring(xml)

    #-------------------------------------------------------------------------------
    #    Process XML Data
    #-------------------------------------------------------------------------------
    obj._process_data(xml_root)

    #-------------------------------------------------------------------------------
    #    If the object has dispatch parameters, flush any remaining records
    #-------------------------------------------------------------------------------
    if hasattr(obj,'dispatch'):
        obj._dispatch_all()

    else:
        #-------------------------------------------------------------------------------
        #    Otherwise return the data structure
        #-------------------------------------------------------------------------------
        return obj.data_structure
    
#-------------------------------------------------------------------------------
#    When module is executed as a script
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    
    def to_upper(value):
        pp(value)
        return value.upper()

    #-------------------------------------------------------------------------------
    #    Define a profile
    #-------------------------------------------------------------------------------
    profile = """
    catalog
        shop
            book
                author = dataset:title_and_author
                title  = dataset:title_and_author
    """    

    #-------------------------------------------------------------------------------
    #    Define XML
    #-------------------------------------------------------------------------------
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

    #-------------------------------------------------------------------------------
    #    Call parse_using_profile
    #-------------------------------------------------------------------------------
    parse_using_profile(xml, profile)
