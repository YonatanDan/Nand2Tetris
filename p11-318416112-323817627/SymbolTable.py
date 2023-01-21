class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.subroutines_scope = {}
        self.current_scope = self.class_scope 
        self.counters_dict = {
            'static': 0,
            'field': 0,
            'arg': 0,
            'var': 0,
            'if': 0,
            'while': 0
        }
    
    def reset(self):
        for kind in self.counters_dict:
            if kind not in ['static', 'field']:
                self.counters_dict[kind] = 0

    def add_subroutine(self, subr_name):
        self.subroutines_scope[subr_name] = {}

    def define(self, name, type, kind):
        if kind in ['static', 'field']:
            self.class_scope[name] = (type, kind, self.counters_dict[kind])
            self.counters_dict[kind] += 1
        elif kind in ['arg', 'var']:
            self.current_scope[name] = (type, kind, self.counters_dict[kind])
            self.counters_dict[kind] += 1
    
    def class_count(self, kind):
        return len([tuple for (name, tuple) in self.class_scope.items() if tuple[1] == kind])
    
    def var_count(self, kind):
        return len([tuple for (name, tuple) in self.current_scope.items() if tuple[1] == kind])

    def kind_of(self, name):
        if name in self.current_scope:
            return self.current_scope[name][1]
        elif name in self.class_scope:
            return self.class_scope[name][1]
        else:
            return 'NONE'        

    def type_of(self, name):
        if name in self.current_scope:
            return self.current_scope[name][0]
        elif name in self.class_scope:
            return self.class_scope[name][0]

    def index_of(self, name):
        if name in self.current_scope:
            return self.current_scope[name][2]
        elif name in self.class_scope:
            return self.class_scope[name][2]

    def set_scope(self, subr_name):
        if subr_name == 'class':
            self.current_scope = self.class_scope
        else:
            self.current_scope = self.subroutines_scope[subr_name]                

        