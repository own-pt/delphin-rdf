from typing import Union
from typing import Iterator

from itertools import repeat, count

from rdflib import Graph
from delphin.rdf import mrs_to_rdf

CODEC_INFO = {
    'representation': 'mrs',
    'description': 'RDF formated MRS'
}

##############################################################################
## Serialization Functions

def dump(ms, destination, prefix:str, identifiers=None, texts=None,
         format:str="turtle", lnk=True, properties=True, indent=False,
         encoding='utf-8'):

    """
    Serialize a MRS iterable to RDF. 

    Args:
        ms - iterable of MRS objects
        destination - path-like object or file object where data
        will be written to
        prefix - an URI string to be used as prefix
        identifiers - an Iterable of Strings or Iterables of strings
        identifying the mrs. It should be unique. For instance, one
        may use it as [textid, mrs-id] if same text admits various
        mrs interpretations. If None is given, than uses a sequence
        if integers as identifiers.
        texts - an Iterable of texts to be represented in MRS as RDF.
        format - file format to serialize the output into.
    """
    
    graph = _encode(ms=ms, prefix=prefix, identifiers=identifiers, texts=texts)
    graph.serialize(destination=destination, format=format, encoding=encoding)


def dumps(ms, prefix:str, identifiers=None, texts=None, format:str="turtle",
          lnk=True, properties=True, indent=False, encoding='utf-8'):
    """
    Serialize MRS objects to RDF and return the string.

    Args:
        ms - iterable of MRS objects
        destination - path-like object or file object where data
        will be written to
        prefix - an URI string to be used as prefix
        identifiers - an Iterable of Strings or Iterables of strings
        identifying the mrs. It should be unique. For instance, one
        may use it as [textid, mrs-id] if same text admits various
        mrs interpretations. If None is given, than uses a sequence
        if integers as identifiers.
        texts - an Iterable of texts represented in mrs as RDF.
        format - file format to serialize the output into.
    """
    
    graph = _encode(ms=ms, prefix=prefix, identifiers=identifiers, texts=texts)
    return graph.serialize(format=format, encoding=encoding).decode("ascii")

def encode(m, prefix:str, identifier=None, format:str="turtle",
           text:str=None, properties=True, lnk=True, indent=False):
    """
    Serialize a single MRS object to a RDF string

    Args:
        m - a single MRS object
        prefix - an URI string to be used as prefix
        identifier - an string or iterable of string identifying
        the mrs. It should be unique. For instance, one may use
        it as [textid, mrs-id] if the same text admits various
        mrs interpretations.
        text - the text that is represented in MRS as RDF. 
        format - file format to serialize the output into.

    Returns:
        An RDF representation of the MRS object
    """
    # properties - if False, suppress morphosemantic properties
    # lnk - if False, suppress surface alignments and strings
    # indent - if True, add newlines and indentation

    graph = _encode(ms=[m],prefix=prefix,identifiers=[identifier],texts=[text])
    return graph.serialize(format=format).decode("ascii")
 
def _encode(ms, prefix:str, identifiers, texts:str=None, properties=True,
            lnk=True, indent=False, encoding='utf-8'):
    """
    Returns a rdflib Graph containing RDF representations of ms

    Args:
        ms - iterable of MRS objects
        prefix - an URI string to be used as prefix
        identifiers - an Iterable of Strings of Iterables-of-Strings
        identifying the mrs. It should be unique. For instance, one
        may use it as [textid, mrs-id] if same text admits various
        mrs interpretations. If None is given, than uses a sequence
        if integers as identifiers. 
        texts - an Iterable of texts represented in mrs as RDF.
        format - file format to serialize the output into.

    Returns:
        An RDF representation of the MRS object
    """
    
    # set default iterable identifiers
    if not identifiers: identifiers = count()
    identifiers = iter(identifiers)
    
    # set default iterable texts
    if not texts: texts = repeat(None)
    texts = iter(texts)

    graph = Graph()
    for m in ms:
        text = next(texts)
        identifier = str(next(identifiers))

        graph = mrs_to_rdf(
            m=m, prefix=prefix, graph=graph,
            identifier=identifier, iname="mrs", text=text)

    return graph
##############################################################################
## Deserialization Functions

# def load
# def loads
# def decode