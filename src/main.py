#import parser_extended as parser
import parser

grm = input("gramatics file: ")
# prefix = input("prefixed URI: ")
prefix = "http://example.com/example"

texts = ["the dog barks"]
# texts = [
#     "Two dogs are fighting",
#     "A player is running with the ball",
#     "A skilled person is riding a bicycle on one wheel",
#     "A man in a black jacket is doing tricks on a motorbike",
#     "Two young women are sparring in a kickboxing fight",
#     "Kids in red shirts are playing in the leaves",
#     "A little girl is looking at a woman in costume",
#     "A lone biker is jumping in the air",
#     "A man is jumping into an empty pool",
#     "Four kids are doing backbends in the park",
#     "Two groups of people are playing football"]

def generator(num = 0):
    while True: num +=1; yield num
    
gen = generator(0)

# texts should be any iterable
# gen is an iterable or 
for text in texts:
    identifier = next(gen)
    res = parser.parse(text, prefix, identifier, grm)

    print(res)
    # write output to file
    #with open("{}.nt".format(i+1), "w") as file: file.write(res)