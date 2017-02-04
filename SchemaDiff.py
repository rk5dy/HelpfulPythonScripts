import SchemaDoc
import re
import itertools

attributes = ['path', 'name', 'minOccurs', 'maxOccurs', 'type', 'minLength', 'maxLength', 'Change Type', 'Change Value']

xsd1 = [re.sub(r'/+', '/', line).split(',') for line in SchemaDoc.MakeCSVArray("")[0][1]]
xsd2 = [re.sub(r'/+', '/', line).split(',') for line in SchemaDoc.MakeCSVArray("")[0][1]]
xsd1FieldUris = list(zip(*xsd1))[0]
xsd2FieldUris = list(zip(*xsd2))[0]

removed = [a for a in xsd1FieldUris if a not in xsd2FieldUris]

added = [a for a in xsd2FieldUris if a not in xsd1FieldUris]

commonFieldsXsd1 = [element for element in xsd1 if element[0] not in removed]
commonFieldsXsd2 = [element for element in xsd2 if element[0] not in added]
commonFields = list(zip(*(commonFieldsXsd1, commonFieldsXsd2)))
changed = []
for a, b in commonFields:
    diffString = ''
    if a != b:
        comparisons = list(zip(*(attributes, a, b)))
        for attName, aAttr, bAttr in comparisons:
            if aAttr != bAttr:
                if aAttr == "":
                    aAttr = "Nothing"
                if bAttr == "":
                    bAttr = "Nothing"
                diffString += "{0}: {1} => {2},".format(attName, aAttr, bAttr)
        changed.append((b[0], diffString))

changedPaths = list(list(zip(*(changed)))[0])
changedMappings = {a[0]:a[1] for a in changed}
#print(changedPaths)
#print(changedMappings)

print(','.join(attributes))
for row in xsd2:
    line = ','.join(row[:-1])
    if row[0] in added:
        print(line + ',Added')
    elif row[0] in changedPaths:
        print("{0},Changed,{1}".format(line, changedMappings[row[0]]))
    else:
        print("{0},None".format(line))

[print("{0},Removed".format(','.join(row[:-1]))) for row in xsd1 if row[0] in removed]

#finalcsv = [["" if a == None else a for a in row] for row in tmpFinalCsv]
#print(finalcsv)
#[print(','.join(a)) for a in finalcsv]
