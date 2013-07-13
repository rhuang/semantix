import unittest
import sys, os

#os.path.dirname(__file__) returns back the path to the directory containing
# __file__, which refers to the file which was called in the console
# in this case it is test_locationUnitTest. __file__ does not need to be
# a single file name it can be a relative or absolute path, as well, to some
# directory for example

#os.path.abspath(__file__) returns back the path including the file which was
# called in the console

sys.path.insert(0, os.path.dirname(__file__)+"\\..")
import stringsimilarity


def filterDuplicateAddresses(addresses):
    filteredAddresses = []
    for address1 in addresses[:]:
        if address1 not in addresses:
            break
        addresses.remove(address1)
        for address2 in addresses[:]:
            similarity = stringsimilarity.compute(address1, address2)
            if similarity > 0.6:
                addresses.remove(address2)
                if len(address2) > len(address1):
                    address1 = address2
        filteredAddresses.append(address1)
    return filteredAddresses


class TestSequenceFunctions(unittest.TestCase):

    def test_filter_two_of_the_same_address(self):
        addresses = ["9 Tong Yin Street, Tseung Kwan O, New Territories Shop Unit F10, Popcorn Hong Kong, (852)-3902-3875", 
                     "9 Tong Yin Street, Tseung Kwan O, New Territories Hong Kong - TKO Shop Unit F10, Popcorn Hong Kong,"]
    
        expected = ["9 Tong Yin Street, Tseung Kwan O, New Territories Shop Unit F10, Popcorn Hong Kong, (852)-3902-3875"]
        
        self.assertEqual(filterDuplicateAddresses(addresses), expected)
        
    def test_filter_two_addresses_one_with_more_detail(self):
        addresses = ["180 El Camino Real Palo Alto, CA 94304",
                      "180 El Camino Real Stanford Shopping Center - Now Open Palo Alto, CA 94304"]
                      
        expected = ["180 El Camino Real Stanford Shopping Center - Now Open Palo Alto, CA 94304"]
        
        self.assertEqual(filterDuplicateAddresses(addresses), expected)

    def test_increasing_details_same_address(self):
        addresses = ["123 fake", "123 fake st", "123 fake st kitchener",
                     "123 fake st kitchener, ontario", 
                     "123 fake st kitchener, ontario st",
                     "123 fake", "123 fake st"]
        
        expected = ["123 fake st kitchener, ontario st"]
        
        self.assertEqual(filterDuplicateAddresses(addresses), expected)