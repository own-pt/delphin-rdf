import os

from rdflib import Graph

from delphin import ace
from delphin.web import client
from delphin.rdf import parser
# import parser as p

def text_to_rdf(text, prefix, identifier, grm=None, out=None, format="turtle"):
    """
    Receives a text and parses it into RDF format.

    text - the text to be parsed.

    grm - a grammar to be used to parse the texts.
    
    prefix - the URI to be prefixed to the RDF formated mrs.
    
    identifier - an string or a list of strings identifying
    the mrs. It should be unique, possibly using a composite
    identifier, given in list.
    For instance one may use it as [textid, mrs-id] if the
    same text admits various mrs interpretations.

    out - filename to serialize the output into.

    format - file format to serialize the output into.
    """

    if grm:
        response = ace.parse(grm, text)
        for result in response.result():
            m = result.mrs()
            g = p.mrs_to_rdf(m, )
    else:
        pass

def file_to_rdf(path, grm, prefix, identifier=None, out=None, format="turtle"):
    """
    Receives a path to a single text file and attemps to
    parse them into RDF format.
    
    path - path to the texts file.
    
    grm - a grammar to be used to parse the texts.
    
    prefix - the URI to be prefixed to the RDF formated mrs.
    
    identifier - an string or a list of strings identifying
    the mrs. It should be unique, possibly using a composite
    identifier, given in list.
    For instance one may use it as [textid, mrs-id] if the
    same text admits various mrs interpretations.

    out - filename to serialize the output into.

    format - file format to serialize the output into.
    """

    pass

def path_to_rdf(path, grm, prefix, identifier=None, out=None, format="turtle"):
    """
    Receives a path to a text file or container of texts
    files and attemos to parse them into RDF format. It
    may be usefull when parsing from a text corpus.

    path - path to the file or container.
    
    grm - a grammar to be used to parse the texts.
    
    prefix - the URI to be prefixed to the RDF formated mrs.
    
    identifier - an string or a list of strings identifying
    the mrs. It should be unique, possibly using a composite
    identifier, given in list.
    For instance one may use it as [textid, mrs-id] if the
    same text admits various mrs interpretations.

    out - filename to serialize the output into.

    format - file format to serialize the output into.
    """
    
    # we should define an user interface to chose the
    # best mrs format to be parsed, or add an option
    # to parse all interpretations.

    # it should be usefull to parse each file or text
    # into a single output

    if os.path.isdir(path):
        for f in os.listdir(path):
            print(path+"/"+f)
    else:
        print(path)