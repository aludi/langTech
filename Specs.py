


class Specification:
    ###here we can store all relevant specifications, for now i have question words (not used) and regex patterns with corresponding object - property - result order
    ###takes a dictionary as input
    def __init__(self, specList):
        self.ignored_words = specList['ignored_words']
        self.question_words = specList['question_words']
        self.patterns = specList['patterns']
        self.deps = specList['deps']
        self.basic_question_formats = specList['basic_question_formats']
        self.extended_deps = specList['extended_deps']
        self.true_false_list = specList['true_false_list']
        self.count_list = specList["count_list"]
        self.tags_of_interest = specList['tags_of_interest']
        self.prints = specList["print"]
        self.common_IDs = specList["common_IDs"]

    def printConditional(self, string):
        if self.prints:
            prints(string)
