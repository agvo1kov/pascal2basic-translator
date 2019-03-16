class Analyzer:
    state = 'S'
    string = ''
    collecting_string = ''

    listw = [1, 2, 4, ]
    
    def __init__(self, string):
        self.string = string
        
    def reset(self):
        self.collecting_string = ''
        self.state = 'S'
        
    def unexpected(self, symbol):
        self.state = 'error'
        print(Back.RED, Fore.WHITE,'ERRORE!', Style.RESET_ALL, 'Unexpected symbol \"' + symbol + '\"')
        return {
            'kind': 'error',
            'token': symbol,
            'residue': ''
        }
    
    def symbol_return(self, symbol):
        self.string = symbol + self.string
        if symbol != '':
            self.collecting_string = self.collecting_string[:-1]
    
    def collect_next(self):
#         print('String: "',  end='')
#         print(Fore.BLUE + self.string + Style.RESET_ALL, end='')
#         print('"')
        
        try:
            symbol = self.string[0]
            self.string = self.string[1:]
        except:
            symbol = ''
        self.collecting_string += symbol
        
        if self.state == 'S':
            if symbol.isalpha() or symbol == '_':
                self.state = 'letter_at_first'
            elif symbol == '<':
                self.state = '<_at_first'
            elif symbol == '>':
                self.state = '>_at_first'
            elif symbol in operations:
                return {
                    'kind': 'operation',
                    'token': symbol,
                    'residue': self.string
                }
            elif symbol.isdigit():
                self.state = 'digit_at_first'
            elif symbol == '.':
                self.state = '._at_first'
            return self.collect_next()
        
        if self.state in ['number -> .. -> number']:
            if symbol.isdigit():
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'integer_interval',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)
        
        if self.state in ['number -> ..']:
            if symbol.isdigit():
                self.state = 'number -> .. -> number'
                return self.collect_next()
            else:
                return self.unexpected(symbol)
        
        if self.state == 'digit_at_first':
            if symbol.isdigit():
                return self.collect_next()
            elif symbol == '.':
                self.state = 'number -> .'
                return self.collect_next()
            elif symbol == 'e':
                self.state = 'number -> e'
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'integer',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)
            
        if self.state == 'number -> .':
            if symbol == '.':
                self.symbol_return(symbol)
                self.symbol_return(symbol)
                return {
                    'kind': 'integer',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            
        if self.state == '._at_first':
            if symbol == '.':
                return {
                    'kind': 'separator',
                    'token': self.collecting_string,
                    'residue': self.string
                }
        
        if self.state in ['._at_first', 'number -> .']:
            if symbol.isdigit():
                return self.collect_next()
            elif symbol == 'e':
                self.state = 'number -> e'
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'real',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            elif symbol == '.':
                self.state = 'number -> ..'
                return self.collect_next()
            else:
                return self.unexpected(symbol)
                
        if self.state == 'number -> e':
            if symbol in ['+', '-']:
                self.state = 'number -> e -> +/-'
                return self.collect_next()
            elif symbol.isdigit():
                self.state = 'number -> e -> digit'
                return self.collect_next()
            else:
                return self.unexpected(symbol)
        
        if self.state in ['number -> e -> +/-', 'number -> e -> digit']:
            if symbol.isdigit():
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'real',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)
                
        if self.state == '<_at_first':
            if symbol in ['>', '=']:
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                self.symbol_return(symbol)
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }
        
        if self.state == '>_at_first':
            if symbol == '=':
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                self.symbol_return(symbol)
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }
        
        if self.state == 'letter_at_first':
            if symbol.isalpha() or symbol.isdigit() or symbol == '_':
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'identifier',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)
            
        return {
            'kind': 'exeption',
            'token': str(self.state),
            'residue': self.string
        }