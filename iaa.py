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


def xml_to_triples(filename, tag_filter):
    id_to_location = {}
    description_triples = []
    action_triples = []
    relation_triples = []
    malformed_tags = []

    annotator_id = filename.split("/")[-1].split(".")[0]
    main = ET.parse(filename).getroot().find("TemporalDirections")
    if main is not None:
        tags = main.find("TAGS")
        if tags is not None:
            for tag in sorted(tags, key=lambda t: t.tag):
                if tag.tag != "RELATION" and tag_filter(tag):
                    location = "{}.{}~{}.{}".format(tag.attrib["span_start_line"],
                                                    tag.attrib["span_start_char"],
                                                    tag.attrib["span_end_line"],
                                                    tag.attrib["span_end_char"])
                    id_to_location[tag.attrib["id"]] = location
                    if tag.tag == "DIRECTION":
                        try:
                            description_triples.append([annotator_id, location, tag.attrib["description"]])
                            action_triples.append([annotator_id, location, tag.attrib["action"]])
                        except:
                            malformed_tags.append(tag)
                else:
                    try:
                        fromLocation = id_to_location[tag.attrib["fromID"]]
                        toLocation = id_to_location[tag.attrib["toID"]]
                        location = "{}-{}".format(fromLocation, toLocation)
                        relation_triples.append([annotator_id, location, tag.attrib["relationship"]])
                    except:
                        malformed_tags.append(tag)
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
        return tagged_start_line_count == total_annotators and tagged_end_line_count == 3
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

task = AnnotationTask(data=triples[0])
print(task.C)
print(task.multi_kappa())
print(task.alpha())
