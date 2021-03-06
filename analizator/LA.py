import pickle
from EpNKA import EpNKA
import sys


class LexicalAnalyzer:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path  # file with analyzer states and corresponding automata indices and function parameters
        self.input = ""  # input file text
        self.automata = []  # automata at indices corresponding to their rule numbers
        self.first_state = "" # first analyzer state
        self.curr_state = ""  # current analyzer state
        self.state_map = {}  # maps rule indices to analyzer states
        self.rule_map = {}  # maps rule parameters to indices
        self.line_cnt = 1  # counts lines in input document
        self.begin = 0  # index of first unanalyzed input symbol
        self.end = -1  # index of last analyzed input symbol
        self.last = -1  # index of last recognized input symbol
        self.curr_rule = -1  # last recognized rule number

        self.configure()
        self.populate_automata()

    def configure(self):  # load confguration for this analyzer
        config_file = open(self.config_file_path, "rb")
        config = pickle.load(config_file)
        self.first_state = config[0]
        self.curr_state = self.first_state
        self.state_map = config[1]
        self.rule_map = config[2]
        config_file.close()

    def populate_automata(self):  # fill list of automata from given directory
        with open('automati.txt', 'r') as file:
            automatonStrings = [x.strip() for x in file.read().split("%E")]
        for a in automatonStrings:
            if a == '':
                continue
            rule_str, automatonDef = a.split("%D\n")
            rule = int(rule_str[3:])
            self.automata.append(EpNKA(rule, automatonDef))

    def apply_rule(self):
        params = self.rule_map[self.curr_rule]
        if params[0] != "-":
            if params[3] != -1:
                print(params[0] + " " + str(self.line_cnt) + " " + self.input[self.begin:self.begin+params[3]])
            else:
                print(params[0] + " " + str(self.line_cnt) + " " + self.input[self.begin:self.last+1])
        if params[1]:
            self.line_cnt += 1
        if params[3] != -1:
            self.begin += params[3]
            self.end = self.begin - 1
        else:
            self.begin = self.last + 1
            self.end = self.last
        self.last = -1
        self.curr_rule = -1
        self.curr_state = params[2]

    def error_recovery(self):
        self.output_error()
        self.end = self.begin
        self.begin += 1

    def output_error(self):
        print(self.input[self.begin] + str(self.line_cnt), file = sys.stderr)

    def feed_automata(self):
        for index in self.state_map[self.curr_state]:
            self.automata[index].giveSymb(self.input[self.end])

    def reset_automata(self):
        for automaton in self.automata:
            automaton.reset()

    def find_valid(self):
        for index in self.state_map[self.curr_state]:
            if self.automata[index].isValid():
                self.curr_rule = index
                self.last = self.end
                return
        return

    def is_empty(self):
        all_empty = True
        for index in self.state_map[self.curr_state]:
            all_empty = all_empty and (self.automata[index].current_states == set())
            if not all_empty:
                break
        return all_empty

    def reset(self):
        self.reset_automata()
        self.input = ""
        self.curr_state = self.first_state
        self.line_cnt = 1
        self.begin = 0
        self.end = -1
        self.last = -1
        self.curr_rule = -1

    def analyze(self):
        f = sys.stdin
        #f = open('CLang_prog.txt')
        self.input = f.read()
        f.close()
        while self.end < len(self.input)-1:
            self.end += 1
            self.feed_automata()
            if self.is_empty():
                if self.last == -1:
                    self.error_recovery()
                else:
                    self.apply_rule()
                self.reset_automata()
            else:
                self.find_valid()
        self.reset()


if __name__ == '__main__':
    LA = LexicalAnalyzer('config')
    LA.analyze()
