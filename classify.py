from collections import Counter
import nltk
import xml.etree.ElementTree as ET
import random

def sent2features(sent):
    return sent[0].split()

def sent2tag(sent):
    return sent[1]

def text_features(text):
    return Counter(text.split())

def xml_to_data(filename):
    description_data = []
    action_data = []
    relation_data = []
    id_to_text = {}

    main = ET.parse(filename).getroot().find("TemporalDirections")
    if main is not None:
        tags = main.find("TAGS")
        if tags is not None:
            for tag in sorted(tags, key=lambda t: t.tag):
                if tag.tag == "DIRECTION":
                    id_to_text[tag.attrib["id"]] = tag.attrib["text"]
                    if "description" in tag.keys():
                        description_data.append((tag.attrib["text"], tag.attrib["description"]))
                    if "action" in tag.keys():
                        action_data.append((tag.attrib["text"], tag.attrib["action"]))
                elif tag.tag == "RELATION":
                    if "fromID" in tag.keys() and tag.attrib["fromID"] in id_to_text:
                        relation_data.append((id_to_text[tag.attrib["fromID"]], tag.attrib["relationship"]))
    return (description_data, action_data, relation_data)

def data_as_features(data):
    return [(text_features(text), label) for (text, label) in data]

def split_data(data, ratio=.7):
    random.shuffle(data)
    n_training = int(len(data)*ratio)
    return (data[:n_training], data[n_training:])

filenames = ["xml_by_annotater/keren.xml",
             "xml_by_annotater/kristen.xml",
             "xml_by_annotater/jingdi.xml"]

(description_data, action_data, relation_data) = ([], [], [])
for filename in filenames:
    data = xml_to_data(filename)
    description_data.extend(data[0])
    action_data.extend(data[1])
    relation_data.extend(data[2])

# Turning training and test sets into feature representations

(train_set, test_set) = split_data(data_as_features(description_data))
classifier = nltk.NaiveBayesClassifier.train(train_set)
print("description:", nltk.classify.accuracy(classifier, test_set))

(train_set, test_set) = split_data(data_as_features(action_data))
classifier = nltk.NaiveBayesClassifier.train(train_set)
print("action:", nltk.classify.accuracy(classifier, test_set))

(train_set, test_set) = split_data(data_as_features(relation_data))
classifier = nltk.NaiveBayesClassifier.train(train_set)
print("relation:", nltk.classify.accuracy(classifier, test_set))
