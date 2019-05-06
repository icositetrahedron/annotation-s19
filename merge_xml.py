import os
import sys
import xml.etree.ElementTree as ET

tag_type = {"DIRECTION": "D", "DIALOGUE": "DI", "RELATION": "R"}
tag_num = {"DIRECTION": 0, "DIALOGUE": 0, "RELATION": 0}

text_segments = []
tags = []

root = ET.Element("root")
doc = ET.SubElement(root, "TemporalDirections")

def standardize(s, standard_tags):
    for id in standard_tags:
        s = s.replace(id, standard_tags[id])
    return s

for dirname, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if filename[0] != "." and filename.endswith(".xml"):
            for child in ET.parse(os.path.join(dirname, filename)).getroot():
                standard_tags = {}
                if child.tag=="TEXT":
                    text = child.text
                    first_line_number = child.text.split()[0].split(",")[0]
                    try:
                        text_segments.append((int(first_line_number), text))
                    except:
                        pass
                elif child.tag=="TAGS":
                    for tag in child:
                        id = tag.items()[0][1]
                        standard_tags[id] = "{}{}".format(tag_type[tag.tag], tag_num[tag.tag])
                        tag_num[tag.tag] += 1
                    for tag in child:
                        for key in tag.keys():
                            tag.set(key, standardize(tag.attrib[key], standard_tags))
                        tags.append(tag)

text_segments.sort()
ET.SubElement(doc, "TEXT").text = "".join(map(lambda t: t[1], text_segments))
ET.SubElement(doc, "TAGS").extend(tags)

tree = ET.ElementTree(root)
tree.write("merged_annotation.xml")
