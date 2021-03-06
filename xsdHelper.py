import xml.etree.ElementTree as etree
import os
import re

#constants
attributes = ['path', 'name', 'minOccurs', 'maxOccurs', 'type', 'minLength', 'maxLength', 'annotations']
primitives = ['int', 'string', 'decimal', 'float', 'dateTime', 'boolean']

#helper method of extracting fields from namespaces
def GetName(nodeTag):
    m = re.match('\{.*?\}(.*?)$', nodeTag)
    if m:
        return m.group(1)
    m = re.match('\(.*?\)(.*?)$', nodeTag)
    if m:
        return m.group(1)
    return nodeTag

def FilterString(s):
    return s[3:] if 'xs' == s[0:2] else s

def MakeCsvRow(uri, field):
    retVal = uri
    for a in attributes[1:]:
        retVal += ','
        if a in field:
            retVal += FilterString(field[a])
    return retVal

def ParseSimpleType(simpleNode):
    baseMap = simpleNode.attrib
    #print(baseMap)
    baseMap['type'] = FilterString(simpleNode[0][0].attrib['base'])
    for n in simpleNode[0][0]:
        if 'min' in n.tag:
            baseMap['minLength'] = n.attrib['value']
        if 'max' in n.tag:
            baseMap['maxLength'] = n.attrib['value']
    #print(baseMap)
    return baseMap

#method to parse sequences
def ParseSequence(sequence, mappings, nameOfBase):
    #print(nameOfBase)
    #print(sequence.tag)
    for e in sequence:
        if 'type' in e.attrib:
            mappings[nameOfBase].append(e.attrib)
        else:
            #print(e.tag)
            mappings[nameOfBase].append(ParseSimpleType(e))
    return mappings

def ParseComplexTypes(root):
    mappings = {}
    complexTypes = [element for element in root if 'complexType' in element.tag]
    for c in complexTypes:
        mappings[c.attrib['name']] = []
        if 'complexContent' in c[0].tag:
            mappings[c.attrib['name']].append({'type' : c[0][0].attrib['base'], 'name' : ''})
            if len(c[0][0]) > 0:
                mappings = ParseSequence(c[0][0][0], mappings, c.attrib['name'])
        else:
            mappings = ParseSequence(c[0], mappings, c.attrib['name'])
    return mappings

#root = root node
#cType = type of node
#uri = current uri
#d = dictionary
#returns list of uris
def TraverseNode(root, cType, uri, d):
    if FieldIsPrimitive(cType):
        return []
    ret = []
    for field in d[cType]:
        currentUri = '{0}/{1}'.format(uri, field['name'])
        ret.append(MakeCsvRow(currentUri, field))
        #print(field)
        ret.extend(TraverseNode(field['name'], field['type'], currentUri, d))
    return ret

def FieldIsPrimitive(field):
	for a in primitives:
		if a in field:
			return True
	return False

#make CSV
def MakeCSVArray(fileName):
    tree = etree.parse(fileName + '.xsd')
    root = tree.getroot()
    complexTypes = [element for element in root if 'complexType' in element.tag]

    #create type mappings
    mappings = ParseComplexTypes(root)
    roots = [element for element in root if 'element' in element.tag]
    retVal = []

    for r in roots:
        retVal.append((r.attrib['name'], TraverseNode(r.attrib['name'], r.attrib['type'], r.attrib['name'], mappings)))
    return retVal

def PrintCSVArray(retVal, fileName):
    for rootName, csvLines in retVal:
        csvFile = open("xsdTrees\\{0}Root{1}.csv".format(fileName, rootName), 'w')
        csvFile.write(",".join(attributes) + '\n')
        newCsvLines = [re.sub(r'/+', '/', line) for line in csvLines]
        csvFile.write('\n'.join(newCsvLines))

files = os.listdir('.\\')

if 'xsdTrees' not in files:
	os.makedirs('.\\xsdTrees')

for a in files:
    m = re.match("(.*?)\.xsd$", a)
    if m:
        print(m.group(0))
        PrintCSVArray(MakeCSVArray(m.group(1)), m.group(1))
