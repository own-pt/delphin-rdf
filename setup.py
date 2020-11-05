#!/usr/bin/env python3

import os
from setuptools import setup

# reading METADATA from __about__.py
about = dict()
base = os.path.dirname(__file__)
path = os.path.join(base, "delphin", "rdf", "__about__.py")
exec(open(path,"r").read(), about)

# reading long description from README.md
long_description = open("README.md","r").read()
 
# defining setup METADATA
setup(
    name=about["__name__"],
    version=about["__version__"],
    description=about["__summary__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=about["__license__"],
    packages=[
       "delphin",
       "delphin.rdf",
       "delphin.cli",
       "delphin.codecs"],
    keywords="delphin pydelphin rdf mrs eds dmrs",
    install_requires=[
       "pydelphin",
       "rdflib"],
    # author=about["__author__"],
    # author_email=about["__email__"],
    # maintainer="",
    # maintainer_email="",
    # url=about["__url__"],
    # download_url="",
    # scripts=[],
    # classifiers=[],
    # platforms="",
)