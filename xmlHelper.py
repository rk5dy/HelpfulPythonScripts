import xml.etree.ElementTree as etree
import os
import re

#helper method of extracting fields from namespaces
def GetName(nodeTag):
    m = re.match('\{.*?\}(.*?)$', nodeTag)
    if m:
        return m.group(1)
    m = re.match('\(.*?\)(.*?)$', nodeTag)
    if m:
        return m.group(1)
    return ""

#helper method for traversing to leaf nodes
def TraverseNode(root, current, ret):
    if len(root) == 0:
        ret.add(current)
        return ret
    tmpret = ret
    for element in root:
        tmp = '{0}/{1}'.format(current, GetName(element.tag))
        tmpret = TraverseNode(element, tmp, ret)
        tmpret.union(ret)
    return tmpret

def ExtractContract(fileName, fieldLoc):
    f = open(fileName, 'r')
    piiFields = set()
    notPii = set()
    for line in f:
        csv = line.strip().split(',')
        if 'Y' in csv and csv[fieldLoc] != '':
            piiFields.add(csv[fieldLoc])
        if 'Y' not in csv and csv[fieldLoc] != '':
            notPii.add(csv[fieldLoc])
    return (piiFields, notPii)

def ExtractXmlLeavesFromDto(fileName):
    tree = etree.parse(fileName)
    root = tree.getroot()
    fieldNodes = TraverseNode(root, GetName(root.tag), set())
    endTags = []
    for a in fieldNodes:
        m = re.match('.*\/(.*?)Field$', a)
        if m:
            endTags.append((a, m.group(1)))
    return endTags

def MakeXMLTree(root, ret, current):
	if len(root) == 0:
		ret.add(current)
		return ret

	tmpret = ret
	for child in root:
		tmp = '{0}/{1}'.format(current, child.tag)
		ret.add(tmp)
		tmpret = makeTree(child, ret, tmp)
		tmpret.union(ret)
	return tmpret
