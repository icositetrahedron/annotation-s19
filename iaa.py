from nltk.metrics.agreement import AnnotationTask
import xml.etree.ElementTree as ET

def xml_to_triples(filename):
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
                if tag.tag != "RELATION":
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
    description_triples = []
    action_triples = []
    relation_triples = []
    for filename in filenames:
        triples = xml_to_triples(filename)
        description_triples.extend(triples[0])
        action_triples.extend(triples[1])
        relation_triples.extend(triples[2])
    return (description_triples, action_triples, relation_triples)

triples = xmls_to_triples(["xml_by_annotater/emily.xml",
                           "xml_by_annotater/keren.xml",
                           "xml_by_annotater/kristen.xml",
                           "xml_by_annotater/jingdi.xml"])

print(triples[0])
task = AnnotationTask(data=triples[0])
print(task.C)
print(task.kappa())
print(task.alpha())
