# dict tablica bi izgledala ovako:
# {'neki_idn': TabZnakEntry1, 'neki_drugi_idn': TabZnak2 ...}
class TablicaZnakova:
    def __init__(self, parent=None):
        self.parent = parent
        self.tablica = dict()
    
    def add(self, key, entry):
        if key not in self.tablica:
            self.tablica[key] = entry
            return True
        return False
    
    def get(self, key, default=False):
        if key in self.tablica:
            return self.tablica[key]
        return default

    def update(self, key, entry):
        self.tablica[key] = entry
        return True
    
    def idn_declared(self, idn):
        if idn in self.tablica:
            return self.tablica[idn]
        elif self.parent:
            return self.parent.idn_declared(idn)
        
        return False  # If this is root and no identificator return False

    def function_defined(self, idn):
        if idn in self.tablica:
            return self.tablica[idn].defined
        elif self.parent:
            return self.parent.function_defined(idn)

        return False
    
    def get_idn_and_other_info(self, key):
        level = 0
        is_global = False
        curr_tablica_znakova = self
        while key not in curr_tablica_znakova.tablica:
            curr_tablica_znakova = curr_tablica_znakova.parent
            level += 1
        if curr_tablica_znakova.parent == None: is_global = True
        return curr_tablica_znakova.tablica[key], level, is_global
        
    
# Po potrebi u ovu klasu dodavat razne atribute koji su potrebni
class TabZnakEntry:
    def __init__(self, tip, lizraz=False, defined=False):
        self.tip = tip          # npr. 'int' ili 'char'
        self.lizraz = lizraz
        self.defined = defined
        self.label = None
        self.pointer = False