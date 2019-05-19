#!/usr/bin/python3

###############################################
# NBT File Parser                             #
# Follows the Named Binary Tag Specifications #
# as defined by Marcus Persson                #
###############################################

import struct
import gzip

def read_nbt(path):
    with gzip.open(path, 'rb') as nbt:
        result = {}
        decode_nbt(nbt, get_type(nbt), result)
    if '' in result.keys():
        return result['']
    return result

def get_type(nbt):
    return struct.unpack('B', nbt.read(1))[0]

def decode_nbt(nbt, tag_type, data, named=True):
    # TAG_End
    if tag_type == 0:
        return False

    # title is two bytes
    title = ''
    if named:
        title_length = struct.unpack('>h', nbt.read(2))[0]
        for x in range(title_length):
            title += chr(struct.unpack('B', nbt.read(1))[0])

    if tag_type == 1:       # TAG_Byte
        data[title] = struct.unpack('B', nbt.read(1))[0]
    elif tag_type == 2:     # TAG_Short
        data[title] = struct.unpack('>h', nbt.read(2))[0]
    elif tag_type == 3:     # TAG_Int
        data[title] = struct.unpack('>i', nbt.read(4))[0]
    elif tag_type == 4:     # TAG_Long
        data[title] = struct.unpack('>q', nbt.read(8))[0]
    elif tag_type == 5:     # TAG_Float
        data[title] = struct.unpack('>f', nbt.read(4))[0]
    elif tag_type == 6:     # TAG_Double
        data[title] = struct.unpack('>d', nbt.read(8))[0]
    elif tag_type == 7:     # TAG_Byte_Array
        length = struct.unpack('>i', nbt.read(4))[0]
        data[title] = []
        for x in range(length):
            data[title].append(struct.unpack('c', nbt.read(1))[0])
    elif tag_type == 8:     # TAG_String
        length = struct.unpack('>h', nbt.read(2))[0]
        data[title] = ''
        for x in range(length):
            data[title] += chr(struct.unpack('B', nbt.read(1))[0])
        pass
    elif tag_type == 9:     # TAG_List
        sub_type = get_type(nbt)
        length = struct.unpack('>i', nbt.read(4))[0]
        data[title] = []
        TEMPORARY = {}
        for x in range(length):
            decode_nbt(nbt, sub_type, TEMPORARY, False)
            data[title].append(TEMPORARY[''])
    elif tag_type == 10:    # TAG_Compound
        data[title] = {}
        while decode_nbt(nbt, get_type(nbt), data[title]):
            pass
    elif tag_type == 11:    # TAG_Int_Array
        length = struct.unpack('>i', nbt.read(4))[0]
        data[title] = []
        for x in range(length):
            data[title].append(struct.unpack('>i', nbt.read(4))[0])
    elif tag_type == 12:     # TAG_Long_Array
        length = struct.unpack('>i', nbt.read(4))[0]
        data[title] = []
        for x in range(length):
            data[title].append(struct.unpack('>q', nbt.read(8))[0])

    return True


def main():
    import sys, pprint
    fname = sys.argv[1]
    pprint.pprint(read_nbt(fname))

if __name__ == '__main__':
    main()
