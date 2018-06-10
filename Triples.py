from IDfinder import *
class Element:
    ###this is the parent class element, that constructs triples
    def __init__(self, word, isVariable, triple):
        self.isVariable = isVariable            ##if variable, no need to look for id, and the sparql tag will be ?var
        self.word = word
        self.triple = triple                    ##the outside triple is passed so its fields can be set here
        self.SQL = self.stringToSQL()
    def stringToSQL(self):
        ret = ''
        try:
            if self.isVariable:
                ret = '?var' + self.word
                self.triple.variable = ret + ' ' + ret + "Label"
                self.triple.targetVariable = ret + "Label"
            else:
                ret = self.findSQL()
        except:
            print("could not convert '" + self.word + "' into sparql ID")
        return ret

    def setTriple(self):
        pass                                    ##defined in subclasses
    def findSQL(self):
        pass                                    ##defines in subclasses

class Triple:
    def __init__(self, triple, tripleType, specs):

        #print("triple is " + str(triple))
        #print("triple specifictions: " + str(tripleType))

        self.specs = specs
        self.object = type(Object)                  ##These fields will be set later, as we need the order from specs to know which element serves which function
        self.property = type(Property)
        self.result = type(Result)
        self.variable = ''                          ##the names of the variables in the Select statement (will be passed to the questionParser
        self.targetVariable = ''                    ##the names of the variable to be printed (will be passed to the questionParser
        self.parse(triple, tripleType)              ##starts parsing on init
        self.SQL = self.object.stringToSQL() + '  ' + self.property.stringToSQL() + '   ' + self.result.stringToSQL()       ##stores the actual Sparql statement

    def parse(self, triple, tripleType):
        for i in range(0,len(triple)):              ##had to do with indexing, in case there are identical elements in multiple slots
            if isinstance(tripleType[i], dict):                ##if it is a dictionary in the specs, it means that it is the variable
                self.getElement(triple[i],tripleType[i]['variable'],  True)
            else:
                self.getElement(triple[i], tripleType[i], False)

    def getElement(self, word, name, isVariable):
        element = type(Element)
        if name == 'Object':
            element = Object(word, isVariable, self)
        elif name == 'Property':
            element = Property(word, isVariable, self)
        elif name == 'Result':
            element = Result(word, isVariable, self)
        element.setTriple()

    def constructSuperlativeSparql(self, sort):


        self.SQL =  "?superVar   wdt:P31    " + self.object.stringToSQL() + ";\n         " + self.property.stringToSQL() + '   ' + self.result.stringToSQL()
        if sort != None:
            self.SQL +=  ".\n         ?superVar     wdt:" + sort + '   ' + "?sort"
        self.variable = "?superVar  ?superVarLabel"
        self.targetVariable = "?superVarLabel"

        print("var is " + self.variable + "targetvar is " + self.targetVariable)

class Object(Element):

    def findSQL(self):
        return 'wd:' + IDfinder(self.word, 'object', self.triple.specs).findIdentifier()           ##requests a Q ID
    def setTriple(self):
        self.triple.object = self                                               ##sets the triple's Object as itself (same logic for the others)

class Property(Element):

    def findSQL(self):
        return 'wdt:' + IDfinder(self.word, 'property', self.triple.specs).findIdentifier()        ##requests a P ID

    def setTriple(self):
        self.triple.property = self

class Result(Element):

    def findSQL(self):
        return 'wd:' + IDfinder(self.word, 'result', self.triple.specs).findIdentifier()

    def setTriple(self):
        self.triple.result = self
