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
            subfile = ET.parse(os.path.join(dirname, filename)).getroot()
            standard_tags = {}

            if subfile.find("TEXT") is not None or subfile.find("TAGS") is not None:
                annotation = subfile
            elif subfile.find("TemporalDirections") is not None:
                annotation = subfile.find("TemporalDirections")
            else:
                annotation = None

            if annotation is not None:
                source_text = annotation.find("TEXT")
                if source_text is not None and source_text.text is not None:
                    text = source_text.text
                    first_line_number = text.split("\n")[1].split(",")[0]
                    text_segments.append((int(first_line_number), text))

                    source_tags = annotation.find("TAGS")
                    if source_tags is not None:
                        for tag in source_tags:
                            if tag.tag != "RELATION":
                                spans = tag.attrib["spans"].split("~")
                                start = int(spans[0])
                                end = int(spans[1])
                                #print(text_segments[-1][1][start:end], "***", tag.attrib["text"])
                            id = tag.attrib["id"]
                            standard_tags[id] = "{}{}".format(tag_type[tag.tag], tag_num[tag.tag])
                            tag_num[tag.tag] += 1
                        for tag in source_tags:
                            for key in tag.keys():
                                tag.set(key, standardize(tag.attrib[key], standard_tags))
                            tags.append(tag)

text_segments.sort()
ET.SubElement(doc, "TEXT").text = "".join(map(lambda t: t[1], text_segments))
ET.SubElement(doc, "TAGS").extend(tags)

tree = ET.ElementTree(root)
tree.write("merged_annotation.xml")
