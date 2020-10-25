"""
DELPH-IN formats in RDF
"""

from setuptools import setup

setup(
    name="Delphin-RDF",
    version="1.0.0",
    # author="",
    # author_email="",
    # maintainer="",
    # maintainer_email="",
    # url="https://github.com/arademaker/delph-in-rdf",
    # download_url="https://github.com/arademaker/delphin-rdf",
    description=__doc__,
    long_description=open("README.md","r").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    # scripts=[],
    packages=[
       "delphin",
       "delphin.rdf",
       "delphin.cli",
       "delphin.codecs"],
    # classifiers=[],
    # platforms="",
    # keywords="delphin, pydelphin, rdf, mrs, eds, dm, rmrs"
    install_requires=[
       "pydelphin",
       "rdflib"],
)