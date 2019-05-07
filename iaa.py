import re
from csv import reader
from collections import defaultdict
from nltk.metrics.agreement import AnnotationTask
import xml.etree.ElementTree as ET

def get_tagged_lines(filenames):
    id_to_location = {}
    tagged_lines_count = defaultdict(int)

    for filename in filenames:
        tagged_lines = set([])
        main = ET.parse(filename).getroot().find("TemporalDirections")
        if main is not None:
            tags = main.find("TAGS")
            if tags is not None:
                for tag in filter(lambda t: t.tag != "RELATION", tags):
                    tagged_lines.add(tag.attrib["span_start_line"])
                    tagged_lines.add(tag.attrib["span_end_line"])
        for line in tagged_lines:
            tagged_lines_count[line] += 1
    return tagged_lines_count

def line_as_parts(line):
    char_init = len(line[0]) + 1
    return (re.split(r"[()]", line[1]), re.split(r"[()]", line[2]))

def normalize_line_char(line_num, char_num, text):
    #print(line_num, char_num)
    line = list(filter(lambda L: int(L[0])==int(line_num), text))[0]
    char_init = len(line[0]) + 1
    (parts1, parts2) = line_as_parts(line)
    part = -1
    part_start_char = 0
    for i in range(len(parts1)):
        part_end_char = part_start_char + len(parts1[i])
        modified_char_num = int(char_num) - char_init
        if part_start_char <= modified_char_num and modified_char_num <= part_end_char:
            part = i
        part_start_char = part_end_char + 1
    part_start_char += 1
    for i in range(len(parts2)):
        part_end_char = part_start_char + len(parts2[i])
        modified_char_num = int(char_num) - char_init
        if part_start_char <= modified_char_num and modified_char_num <= part_end_char:
            part = len(parts1) + i
        part_start_char = part_end_char + 1
    return "{}.{}".format(line_num, part)

def xml_to_triples(filename, tag_filter):
    id_to_location = {}
    description_triples = []
    action_triples = []
    relation_triples = []
    malformed_tags = []
    tagged_ids = set([])

    annotator_id = filename.split("/")[-1].split(".")[0]
    main = ET.parse(filename).getroot().find("TemporalDirections")
    if main is not None:
        try:
            text = list(filter(lambda L: len(L) == 6 and len(L[0].split())!=0,
                               reader(main.find("TEXT").text.split("\n"))))
        except:
            text = None
        tags = main.find("TAGS")
        if tags is not None and text is not None:
            for tag in sorted(tags, key=lambda t: t.tag):
                if tag.tag != "RELATION" and tag_filter(tag):
                    location = normalize_line_char(tag.attrib["span_start_line"], tag.attrib["span_start_char"], text)
                    id_to_location[tag.attrib["id"]] = location
                    if tag.tag == "DIRECTION":
                        try:
                            description_triples.append((annotator_id, location, tag.attrib["description"]))
                            action_triples.append((annotator_id, location, tag.attrib["action"]))
                            tagged_ids.add(location)
                        except:
                            malformed_tags.append(tag)
                else:
                    try:
                        fromLocation = id_to_location[tag.attrib["fromID"]]
                        toLocation = id_to_location[tag.attrib["toID"]]
                        location = "{}-{}".format(fromLocation, toLocation)
                        relation_triples.append((annotator_id, location, tag.attrib["relationship"]))
                    except:
                        malformed_tags.append(tag)
            for line in text:
                parts = line_as_parts(line)
                parts = parts[0] + parts[1]
                for part in parts:
                    if "{}.{}".format(line, part) not in tagged_ids:
                        description_triples.append((annotator_id, location, "untagged"))
                        action_triples.append((annotator_id, location, "untagged"))
    return (description_triples, action_triples, relation_triples)

def xmls_to_triples(filenames):
    total_annotators = len(filenames)
    description_triples = []
    action_triples = []
    relation_triples = []
    tagged_lines_count = get_tagged_lines(filenames)
    def tag_filter(tag):
        tagged_start_line_count = tagged_lines_count[tag.attrib["span_start_line"]]
        tagged_end_line_count = tagged_lines_count[tag.attrib["span_end_line"]]
        return tagged_start_line_count == total_annotators and tagged_end_line_count == total_annotators
    for filename in filenames:
        triples = xml_to_triples(filename, tag_filter)
        description_triples.extend(triples[0])
        action_triples.extend(triples[1])
        relation_triples.extend(triples[2])
    return (description_triples, action_triples, relation_triples)

filenames = ["xml_by_annotater/keren.xml",
             "xml_by_annotater/kristen.xml",
             "xml_by_annotater/jingdi.xml"]

triples = xmls_to_triples(filenames)


for n in range(3):
    task = AnnotationTask(data=triples[n])
    print(task.C)
    print("kappa:", task.multi_kappa())
    print("alpha:", task.alpha())
