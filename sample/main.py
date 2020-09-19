# this is just a scratch

from delphin import ace
from delphin import eds
from delphin.codecs import eds as edsnative

def parse(grm, text):
    response = ace.parse(grm, text)
    m = response.result(0).mrs()
    return m

text = input("text to parse: ")
grm = input("erg file: ")
parse(text, grm)
