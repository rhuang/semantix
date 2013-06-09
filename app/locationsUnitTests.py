import stringSimilarity

def filterDuplicateAddresses():
    filteredAddresses = []
    for address1 in addresses[:]:
        if address1 not in addresses:
            break
        addresses.remove(address1)
        for address2 in addresses[:]:
            similarity = stringSimilarity.compute(address1, address2)
            if similarity > 0.6:
                addresses.remove(address2)
                if len(address2) > len(address1):
                    address1 = address2
        filteredAddresses.append(address1)
    return filteredAddresses

addresses2 = ["123 fake", "123 fake st", "123 fake st kitchener", "123 fake st kitchener, ontario", "123 fake st kitchener, ontario st", "123 fake", "123 fake st"]
addresses3 = [" 180 El Camino Real Palo Alto, CA 94304", "180 El Camino Real Stanford Shopping Center - Now Open Palo Alto, CA 94304"]
addresses= [" 9 Tong Yin Street, Tseung Kwan O, New Territories Shop Unit F10, Popcorn Hong Kong, (852)-3902-3875", " 9 Tong Yin Street, Tseung Kwan O, New Territories Hong Kong - TKO Shop Unit F10, Popcorn Hong Kong,"]

print filterDuplicateAddresses()