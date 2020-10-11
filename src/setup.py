from setuptools import setup

with open("README.org", "r") as f:
    long_description = f.read()

setup(
   name="Delphin-RDF",
   version="1.0.0",
   url="",
   author="",
   author_email="",
   description="",
   long_description=long_description,
   long_description_content_type="text/org",
   license="MIT",
   scripts=[],
   packages=[
       "delphin",
       "delphin.cli"],
   classifiers=[],
   install_requires=[
       "pydelphin",
       "rdflib"]
)