from Node import Node
from TablicaZnakova import TablicaZnakova, TabZnakEntry
from HelperFunctions import tilda

class Prijevodna_jedinica(Node):
    def __init__(self, data):
        super().__init__(data)
    
    def provjeri(self):
        if self.parent == None:                   # Tablica znakova bi bila None samo u korijenu generativnog stabla, sve ostale prijevodne jedinice naslijedile bi tablicu znakova
            self.tablica_znakova = TablicaZnakova()
        else:
            self.tablica_znakova = self.parent.tablica_znakova
        
        if self.isProduction('<vanjska_deklaracija>'):
            if not self.children[0].provjeri(): return False
        elif self.isProduction('<prijevodna_jedinica> <vanjska_deklaracija>'):
            if not self.children[0].provjeri(): return False
            if not self.children[1].provjeri(): return False
        return True

class Primarni_izraz(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
        self.lizraz = None

    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('IDN'):
            idn_entry = self.get_idn_entry(self.children[0].ime)
            if idn_entry:
                self.tip = idn_entry.tip 
                self.lizraz = idn_entry.lizraz
            else:
                print("<primarni_izraz> ::= IDN({},{})".format(self.children[0].br_linije, self.children[0].ime))
                return False
        elif self.isProduction('BROJ'):
            if not self.children[0].is_valid(): 
                print("<primarni_izraz> ::= BROJ({},{})".format(self.children[0].br_linije, self.children[0].vrijednost))
                return False
            self.tip = 'int'
            self.lizraz = False
        elif self.isProduction('ZNAK'):
            if not self.children[0].is_valid():
                print("<primarni_izraz> ::= ZNAK({},{})".format(self.children[0].br_linije, self.children[0].znak))
                return False
            self.tip = 'char'
            self.lizraz = False
        elif self.isProduction('NIZ_ZNAKOVA'):
            if not self.children[0].is_valid():
                print("<primarni_izraz> ::= NIZ_ZNAKOVA({},{})".format(self.children[0].br_linije, self.children[0].string))
                return False
            self.tip = 'niz(const(char))'
            self.lizraz = False
        elif self.isProduction('L_ZAGRADA <izraz> D_ZAGRADA'):
            if not self.children[1].provjeri(): return False
            self.tip = self.children[1].tip
            self.lizraz = self.children[1].lizraz
        return True


class Vanjska_deklaracija(Node):
    def __init__(self, data):
        super().__init__(data)

    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<definicija_funkcije>'):
            if not self.children[0].provjeri(): return False
        elif self.isProduction('<deklaracija>'):
            if not self.children[0].provjeri(): return False
        
        return True

class Deklaracija(Node):
    def __init__(self, data):
        super().__init__(data)
    
    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<ime_tipa> <lista_init_deklaratora> TOCKAZAREZ'):
            if not self.children[0].provjeri(): return False
            if not self.children[1].provjeri(ntip=self.children[0].tip): return False
        return True

class Lista_init_deklaratora(Node):
    def __init__(self, data):
        super().__init__(data)

    def provjeri(self, ntip):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<init_deklarator>'):
            if not self.children[0].provjeri(ntip=ntip): return False
        elif self.isProduction('<lista_init_deklaratora> ZAREZ <init_deklarator>'):
            if not self.children[0].provjeri(ntip=ntip): return False
            if not self.children[2].provjeri(ntip=ntip): return False
        return True

class Init_deklarator(Node):
    def __init__(self, data):
        super().__init__(data)
    
    def error_in_production2(self):
        production = "<izravni_deklarator> OP_PRIDRUZI({},{}) <inicijalizator>"
        print(production.format(self.children[1].br_linije, self.children[1].val))
    
    def provjeri(self, ntip):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<izravni_deklarator>'):
            if not self.children[0].provjeri(ntip=ntip): return False
            if self.children[0].tip in ['const(int)', 'const(char)', 'niz(const(int))', 'niz(const(char))']:
                print("<init_deklarator> ::= <izravni_deklarator>")
                return False
        elif self.isProduction('<izravni_deklarator> OP_PRIDRUZI <inicijalizator>'):
            if not self.children[0].provjeri(ntip=ntip): return False
            if not self.children[2].provjeri(): return False
            
            if self.children[0].tip in ['int', 'char', 'const(int)', 'const(char)']:
                if self.children[2].tip == None or not tilda(self.children[2].tip, 'T')):
                    self.error_in_production2()
                    return False
            elif self.children[0].tip in ['niz(int)', 'niz(char)', 'niz(const(int))', 'niz(const(char))']:
                if not self.children[2].br_elem or self.children[2].tipovi == None: 
                    self.error_in_production2()
                    return False
                if not self.children[0].br_elem or self.children[2].br_elem > self.children[0].br_elem:
                    self.error_in_production2()
                    return False
                error = False
                for x in self.children[2].tipovi:
                    if not tilda(x, 'T'): error = True
                if error:
                    self.error_in_production2()
                    return False
        
        return True


class Izravni_deklarator(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
        self.br_elem = None
    
    def provjeri(self, ntip):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('IDN'):
            if ntip == 'void' or self.children[0].ime in self.tablica_znakova:
                print("<izravni_deklarator> ::= IDN({},{})".format(self.children[0].br_linije, self.children[0].ime))
                return False
            lizraz = False
            if ntip in ['int', 'char']: lizraz = True
            self.tablica_znakova[self.children[0].ime] = TabZnakEntry(tip=ntip, lizraz=lizraz)
            self.tip = ntip
        elif self.isProduction('IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA'):
            if ntip == 'void' or self.children[0].ime in self.tablica_znakova or int(self.children[2].vrijednost) < 0 or int(self.children[2].vrijednost) > 1024:
                print("<izravni_deklarator> ::= IDN({},{}) L_UGL_ZAGRADA({},{}) BROJ({},{}) D_UGL_ZAGRADA({},{})".format(self.children[0].br_linije, self.children[0].ime, self.children[1].br_linije, self.children[1].val, self.children[2].br_linije, self.children[2].vrijednost, self.children[3].br_linije, self.children[3].val))
                return False
            idn_type = "niz({})".format(ntip)
            self.tablica_znakova[self.children[0].ime] = TabZnakEntry(tip=idn_type, lizraz=False)
            self.tip = idn_type
            self.br_elem = int(self.children[2].vrijednost)
        elif self.isProduction('IDN L_ZAGRADA KR_VOID D_ZAGRADA'):
            f_type = "funkcija(void -> {})".format(ntip)
            if self.children[0].ime in self.tablica_znakova and self.tablica_znakova[self.children[0].ime] != f_type:
                print("<izravni_deklarator> ::= IDN({},{}) L_ZAGRADA({},{}) KR_VOID({},{}) D_ZAGRADA({},{})".format(self.children[0].br_linije, self.children[0].ime, self.children[1].br_linije, self.children[1].val, self.children[2].br_linije, self.children[2].val, self.children[3].br_linije, self.children[3].val))
                return False
            if self.children[0].ime not in self.tablica_znakova: self.tablica_znakova[self.children[0].ime] = TabZnakEntry(tip=f_type, lizraz=False)
        elif self.isProduction('IDN L_ZAGRADA <lista_parametara> D_ZAGRADA'):
            if not self.children[2].provjeri(): return False
            f_type = "funkcija({} -> {})".format(self.children[2].tipovi, ntip)
            if self.children[0].ime in self.tablica_znakova and self.tablica_znakova[self.children[0].ime] != f_type:
                production = "<izravni_deklarator> ::= IDN({},{}) L_ZAGRADA({},{}) <lista_parametara> D_ZAGRADA({},{})"
                print(production.format(self.children[0].br_linije, self.children[0].ime, self.children[1].br_linije, self.children[1].val, self.children[2].br_linije, self.children[2].val))
                return False
            if self.children[0].ime not in self.tablica_znakova: self.tablica_znakova[self.children[0].ime] = TabZnakEntry(tip=f_type, lizraz=False)
        return True

class Inicijalizator(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
        self.br_elem = None
        self.tipovi = None

    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<izraz_pridruzivanja>'):
            if not self.children[0].provjeri(): return False
            izraz_pridruzivanja_zavrsni = self.children[0].get_zavrsni()
            if len(izraz_pridruzivanja_zavrsni) == 1 and izraz_pridruzivanja_zavrsni[0].name = 'NIZ_ZNAKOVA':
                self.br_elem = len(izraz_pridruzivanja_zavrsni[0].string) - 2 + 1  # -2 zbog navodnika + 1 zbog '\0'
                self.tipovi = ['char'] * self.br_elem
            else:
                self.tip = self.children[0].tip
        elif self.isProduction('L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA'):
            if not self.children[0].provjeri(): return False
            self.br_elem = self.children[0].br_elem
            self.tipovi = self.children[0].tipovi
        return True

class Ime_tipa(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None

    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<specifikator_tipa>'):
            if not self.children[0].provjeri(): return False
            self.tip = self.children[0].tip
        elif self.isProduction('KR_CONST <specifikator_tipa>'):
            if not self.children[1].provjeri(): return False
            if self.children[1].tip =='void':
                print('<ime_tipa> ::= KR_CONST({},{}) <specifikator_tipa>'.format(self.children[0].br_linije, self.children[0].val))
                return False
            self.tip = 'const({})'.format(self.children[1].tip)
        return True

class Specifikator_tipa(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
    
    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('KR_VOID'):
            self.tip = 'void'
        elif self.isProduction('KR_CHAR'):
            self.tip = 'char'
        elif self.isProduction('KR_INT'):
            self.tip = 'int'
        else:
            return False
        return True

class Cast_izraz(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
        self.lizraz = None
    
    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<unarni_izraz>'):
            if not self.children[0].provjeri(): return False
            self.tip = self.children[0].tip
            self.lizraz = self.children[0].lizraz
        elif self.isProduction('L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>'):
            if not self.children[1].provjeri(): return False
            if not self.children[3].provjeri(): return False
            brojevni_tipovi = ['const(int)', 'const(char)', 'char', 'int']
            if self.children[1].tip not in brojevni_tipovi or self.children[3].tip not in brojevni_tipovi:  # not super duper sure abt this
                production = '<cast_izraz> ::= L_ZAGRADA({},{}) <ime_tipa> D_ZAGRADA({},{}) <cast_izraz>'
                print(production.format(self.children[0].br_linije, self.children[0].val, self.children[2].br_linije, self.children[2].val))
                return False
            self.tip = self.children[1].tip
            self.lizraz = False
        return True

class Unarni_izraz(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
        self.lizraz = None
    
    def error_in_production_2_or_3(self):
        production = ''
        if self.isProduction('OP_INC <unarni_izraz>'):
            production = '<unarni_izraz> ::= OP_INC({},{}) <unarni_izraz>'
        else:
            production = '<unarni_izraz> ::= OP_DEC({},{}) <unarni_izraz>'
        print(production.format(self.children[0].br_linije, self.children[0].val))

    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<postfiks_izraz>'):
            if not self.children[0].provjeri(): return False
            self.tip = self.children[0].tip
            self.lizraz = self.children[0].lizraz
        elif self.isProduction('OP_INC <unarni_izraz>') or self.isProduction('OP_DEC <unarni_izraz>'):
            if not self.children[1].provjeri(): return False
            if not self.children[1].lizraz or not tilda(self.children[1].tip, 'int'):
                self.error_in_production_2_or_3()
                return False
            self.tip = 'int'
            self.lizraz = False
        elif self.isProduction('<unarni_operator> <cast_izraz>'):
            if not self.children[1].provjeri(): return False
            if not tilda(self.children[1].tip, 'int'):
                print('<unarni_izraz> ::= <unarni_operator> <cast_izraz>')
                return False
            self.tip = 'int'
            self.lizraz = False
        return True

class Unarni_operator(Node):
    def __init__(self, data):
        super().__init__(data)

class Multiplikativni_izraz(Node):
    def __init__(self, data):
        super().__init__(data)
        self.tip = None
        self.lizraz = None
    
    def error_in_group_2(self):
        production = ''
        if self.isProduction('<multiplikativni_izraz> OP_PUTA <cast_izraz>'):
            production = '<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_PUTA({},{}) <cast_izraz>'
        elif self.isProduction('<multiplikativni_izraz> OP_DIJELI <cast_izraz>'):
            production = '<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_DIJELI({},{}) <cast_izraz>'
        else:
            production = '<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_MOD({},{}) <cast_izraz>'
        print(production.format(self.children[1].br_linije, self.children[1].val))

    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<cast_izraz>'):
            if not self.children[0].provjeri(): return False
            self.tip = self.children[0].tip
            self.lizraz = self.children[0].lizraz
        elif self.isProduction('<multiplikativni_izraz> OP_PUTA <cast_izraz>')   or
             self.isProduction('<multiplikativni_izraz> OP_DIJELI <cast_izraz>') or 
             self.isProduction('<multiplikativni_izraz> OP_MOD <cast_izraz>'):

            if not self.children[0].provjeri(): return False
            if not tilda(self.children[0].tip, 'int'):
                self.error_in_group_2()
                return False
            if not self.children[2].provjeri(): return False
            if not tilda(self.children[2].tip, 'int'):
                self.error_in_group_2()
                return False
            self.tip = 'int'
            self.lizraz = False
        return True

class Slozena_naredba(Node):
    def __init__(self, data):
        super().__init__(data)
    
    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA'):
            nova = TablicaZnakova(parent=self.tablica_znakova)
            if not self.children[1].provjeri(new_tablica=nova): return False
        elif self.isProduction('L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA'):
            nova = TablicaZnakova(parent=self.tablica_znakova)
            if not self.children[1].provjeri(new_tablica=nova): return False
            if not self.children[2].provjeri(new_tablica=nova): return False
        return True

class Lista_naredbi(Node):
    def __init__(self, data):
        super().__init__(data)

    def provjeri(self, new_tablica=None):
        if new_tablica:
            self.tablica_znakova = new_tablica
        else:
            self.tablica_znakova = self.parent.tablica_znakova
        
        if self.isProduction('<naredba>'):
            if not self.children[0].provjeri(): return False
        elif self.isProduction('<lista_naredbi> <naredba>'):
            if not self.children[0].provjeri(): return False
            if not self.children[1].provjeri(): return False
        return True

class Lista_deklaracija(Node):
    def __init__(self, data):
        super().__init__(data)
    
    def provjeri(self, new_tablica=None):
        if new_tablica:
            self.tablica_znakova = new_tablica
        else:
            self.tablica_znakova = self.parent.tablica_znakova
        
        if self.isProduction('<deklaracija>'):
            if not self.children[0].provjeri(): return False
        elif self.isProduction('<lista_deklaracija> <deklaracija>'):
            if not self.children[0].provjeri(): return False
            if not self.children[1].provjeri(): return False
        return True

class Naredba(Node):
    def __init__(self, data):
        super().__init__(data)
    
    def provjeri(self):
        self.tablica_znakova = self.parent.tablica_znakova

        if self.isProduction('<slozena_naredba>')  or
           self.isProduction('<izraz_naredba>')    or
           self.isProduction('<naredba_grananja>') or
           self.isProduction('<naredba_petlje>')   or
           self.isProduction('<naredba_skoka>'):
            
            if not self.children[0].provjeri(): return False
        return True