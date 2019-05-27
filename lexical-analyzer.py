#!/usr/bin/env python
# coding: utf-8

# In[2]:


import re
import pprint
import json
from IPython.display import display
from colorama import Fore, Back, Style


# In[3]:


service_words = ['program', 'var', 'const', 'integer', 'real', 'string', 'label',
                 'array', 'of', 'procedure', 'function',
                 'begin', ':=', 'goto', 'if', 'then', 'else', 'end', 'end.', 'return', 'while']
operations = ['+', '-', '*', '/', '^', '<', '>', '=', '<>', '<=', '>=']
separators = [' ', ',', '..', ':', ';', '(', ')', '[', ']', '{', '}', '\'']


# In[4]:


def filter_program(text):
    formatted_text = []
    lines = text.split('\n')
    for index, line in enumerate(lines):
        splitted_text = line.split('\'')
        even_flag = False
        for span in splitted_text:
            if not even_flag:
                formatted_span = re.sub(r'[\t\n]+', ' ', span)
                formatted_span = re.sub(r' +', ' ', formatted_span)
                formatted_span = re.sub(r'\{[.\n]*\}+', '', formatted_span)
                formatted_text.append({
                    'text': formatted_span.lower(),
                    'type': 'code',
                    'line': index + 1
                    
                })
            else:
                formatted_text.append({
                    'text': span,
                    'type': 'string',
                    'line': index + 1
                })

            even_flag = not even_flag
        if not even_flag:
            print(Fore.RED + 'Unexpected end of line. There is unclosed apostrophe!' + Style.RESET_ALL)
            return None
    
#     formatted_text = formatted_text.replace('\\', '\\\\')

    return formatted_text
        


# In[5]:


class Analyzer:
    state = 'S'
    string = ''
    collecting_string = ''
    
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


# In[6]:


def split_by_separator(line):
    global separators
    
#     Search first separator or assignment
    first_separator_index = len(line)
    for character in line:
        if character in separators:
            first_separator_index = line.index(character)
            break
    
#   Token kind determinination
    token = line[:first_separator_index]
    separator = ''
    if first_separator_index < len(line):
        separator = line[first_separator_index]
    
    kind = 'unknown'
    if token in service_words:
        kind = 'service_word'
    elif token in operations:
        kind = 'operation'
        
#     Checking for String
    elif not token and separator == '\'':
        kind = 'string'
        
#         Search second apostrophe
        second_apostrophe_index = 1
        if len(line) > 1:
            while line[second_apostrophe_index] != '\'' and second_apostrophe_index < len(line):
                second_apostrophe_index+=1
                
#         Slicing string constant from line
        token = line[1:second_apostrophe_index]
        separator = '\''
        first_separator_index = second_apostrophe_index-1
        
        return {
            'token': token,
            'kind': kind,
            'separator': separator,
            'remaining_line': line[second_apostrophe_index+1:]
        }
#     Assignment regognition
    elif not token and separator == ':' and line[first_separator_index+1] == '=':
        kind = 'service_word'
        token = ':='
        separator = ''
        first_separator_index+=1
        
    else:
#         Checking for Int, Real, Indetifier
        try:
            int(token)
            kind = 'integer'
        except:
            kind = 'unknown'
    
#     Preparation to detect assignment operator
    if separator == ':':
        try:
            if line[first_separator_index+1] == '=':
                separator = ''
                first_separator_index-=1
        except:
            pass
        
    if separator == '\'':
        first_separator_index-=1
    
    try:
        if line[first_separator_index+1] == '\'' and (not separator.isspace()) and separator != '\'':
            line = line[:first_separator_index+1] + ' ' + line[first_separator_index+1:]
        elif line[first_separator_index+1] == '\'' and separator.isspace():
            separator = '\'';
    except:
        pass

    return {
        'token': token,
        'kind': kind,
        'separator': separator,
        'remaining_line': line[first_separator_index+1:]
    }


# In[7]:


def append_consumable(token, kind, number_of_procedure=0, level_of_procedure=0, number_in_procedure=0):
    global constants
    global identifiers
    
    if kind in ['integer', 'real', 'string', 'integer_interval']:
        constant = {
            'type': kind,
            'value': token
        }
        if not constant in constants:
            constants.append(constant)
    elif kind == 'identifier':
        identifier = {
            'type': kind,
            'name': token,
            'number_of_procedure': number_of_procedure,
            'level_of_procedure': level_of_procedure,
            'number_in_procedure': number_in_procedure
        }
        if not identifier in identifiers:
            identifiers.append(identifier)


# In[8]:


def to_token_analyze(file_name):
    global tokens_chain
    
    program = filter_program(open(file_name).read())
    print(program)
    
    if not program:
        return None
    
#     print(Fore.BLUE, program, Style.RESET_ALL)

    tokens_chain = []
    
    program_context_flag = False
    var_context_flag = False
    array_context_flag = False
    label_context_flag = False
    function_context_flag = False
    procedure_context_flag = False
    var_pool = []

    for segment in program:
        if segment['type'] == 'code':
#             for line in lines:
            remaining_line = segment['text']
            splitted_line = split_by_separator(remaining_line)
            while remaining_line:
                token = splitted_line['token']
                kind = splitted_line['kind']
                separator = splitted_line['separator']
                remaining_line = splitted_line['remaining_line']

                kind_suffix = ''
                if token or kind == 'string':                
                    if kind == 'service_word':                        
                        tokens_chain.append([
                            'W',
                            service_words.index(token),
                            token,
                            segment['line']
                        ])
                        kind_suffix = 'W' + str(service_words.index(token))

                        if token == 'array':
                            array_context_flag = True
                        else:
                            if token in ['integer', 'real', 'string']:
                                var_type = token
                                if array_context_flag:
                                    var_type += '_array';

                                for var in var_pool:
                                    identifiers[:] = [d for d in identifiers if d.get('name') != var]
                                    identifiers.append({
                                        'type': var_type,
                                        'name': var,
                                        'number_of_procedure': 0,
                                        'level_of_procedure': 0,
                                        'number_in_procedure': 0
                                    })
                                var_pool = []
                                array_context_flag = False

                            elif token != 'of':
                                if token == 'var':
                                    var_context_flag = True
                                else:
                                    var_context_flag = False

                                if token == 'program':
                                    program_context_flag = True
                                else:
                                    program_context_flag = False

                                if token == 'label':
                                    label_context_flag = True
                                else:
                                    label_context_flag = False

                                if token == 'function':
                                    print(Fore.BLUE + 'FUNCTION', Fore.BLACK + 'context ON', Style.RESET_ALL)
                                    function_context_flag = True
                                
                                if token == 'procedure':
                                    print(Fore.BLUE + 'PROCEDURE', Fore.BLACK + 'context ON', Style.RESET_ALL)
                                    procedure_context_flag = True
                                    

                    elif kind == 'operation':
                        tokens_chain.append([
                            'O',
                            operations.index(token),
                            token,
                            segment['line']
                        ])
                        kind_suffix = 'O' + str(operations.index(token))

                    if kind == 'unknown':

    #                     Automat analyze

                        automat = Analyzer(token)
                        residue = token

                        while residue:
                            automat.reset()
                            analyzed = automat.collect_next()
                            kind = analyzed['kind']
                            token = analyzed['token']
                            residue = analyzed['residue']

                            if kind == 'exeption':
                                print(Fore.BLACK + '\"' + token + '\"', Fore.RED + kind, Fore.WHITE + 'by analyzer' + Style.RESET_ALL, residue)
                            else:

    #                             Var pool
                                if kind == 'identifier' and (var_context_flag or program_context_flag or label_context_flag or function_context_flag or procedure_context_flag):
                                    var_pool.append(token)

    #                             New identifier
                                if kind == 'identifier' and not len([d for d in identifiers if d.get('name') == token]):
                                    append_consumable(token, kind)                                


    #                             Constant
                                if kind in ['integer', 'real', 'string']:
                                    append_consumable(token, kind)
                                    for index, constant in enumerate(constants):
                                        if constant['value'] == token:
                                            break
                                    tokens_chain.append([
                                        'C',
                                        index,
                                        constant['value'],
                                        segment['line']
                                    ])
                                    kind_suffix = 'C' + str(index)

    #                             Identifier
                                elif kind == 'identifier':
                                    for index, identifier in enumerate(identifiers):
                                        if identifier['name'] == token:
                                            break
                                    tokens_chain.append([
                                        'I',
                                        index,
                                        identifier['name'],
                                        segment['line']
                                    ])
                                    kind_suffix = 'I' + str(index)

    #                             Separator
                                elif kind in ['separator']:
                                    tokens_chain.append([
                                        'R',
                                        separators.index(token),
                                        token,
                                        segment['line']
                                    ])
                                    kind_suffix = 'R' + str(separators.index(token))

    #                             Operation
                                elif kind in ['operation']:
                                    tokens_chain.append([
                                        'O',
                                        operations.index(token),
                                        token,
                                        segment['line']
                                    ])
                                    kind_suffix = 'O' + str(operations.index(token))
                                print(Fore.BLACK + '\"' + token + '\"', Fore.GREEN + kind, Fore.WHITE + 'by analyzer' + Style.RESET_ALL, kind_suffix, Back.WHITE + 'line #' + str(segment['line']) + Style.RESET_ALL)

                    else:
    #                     Pre-recognized constants or handled service words
                        if kind in ['integer', 'string']:
                            append_consumable(token, kind)
                            for index, constant in enumerate(constants):
                                if constant['value'] == token:
                                    break
                            tokens_chain.append([
                                'C',
                                index,
                                constant['value'],
                                segment['line']
                            ])
                            kind_suffix = 'C' + str(index)
                        print(Fore.BLACK + '\"' + token + '\"', Fore.GREEN + kind, Style.RESET_ALL + kind_suffix + ' ' + Back.WHITE + 'line #' + str(segment['line']) + Style.RESET_ALL)

                if not separator.isspace():
                    if separator == ';':
                        if program_context_flag:
                            var_type = 'program'
                        else:
                            var_type = 'identifier'
                        if array_context_flag:
                            var_type += '_array';

                        for var in var_pool:
                            identifiers[:] = [d for d in identifiers if d.get('name') != var]
                            identifiers.append({
                                'type': var_type,
                                'name': var,
                                'number_of_procedure': 0,
                                'level_of_procedure': 0,
                                'number_in_procedure': 0
                            })
                        var_pool = []
                            
                    if separator in separators and separator != ' ':
                        tokens_chain.append([
                            'R',
                            separators.index(separator),
                            separator,
                            segment['line']
                        ])
                        print(Fore.BLACK + '\"' + separator + '\"', Fore.GREEN + 'separator', Style.RESET_ALL + 'R' + str(separators.index(separator)) + ' ' + Back.WHITE + 'line #' + str(segment['line'])+ Style.RESET_ALL)
                        if separator == ';':
                            print()
                            
                    if separator == '(' and function_context_flag:
                        print(Fore.BLUE + 'FUNCTION', Fore.BLACK + 'context OFF', Style.RESET_ALL)
                        identifiers[:] = [d for d in identifiers if d.get('name') != var_pool[0]]
                        identifiers.append({
                            'type': 'function',
                            'name': var_pool[0],
                            'number_of_procedure': 0,
                            'level_of_procedure': 0,
                            'number_in_procedure': 0
                        })
                        var_pool = []
                        function_context_flag = False
                    
                    if separator == '(' and procedure_context_flag:
                        print(Fore.BLUE + 'PROCEDURE', Fore.BLACK + 'context OFF', Style.RESET_ALL)
                        try:
                            identifiers[:] = [d for d in identifiers if d.get('name') != var_pool[0]]
                            identifiers.append({
                                'type': 'procedure',
                                'name': var_pool[0],
                                'number_of_procedure': 0,
                                'level_of_procedure': 0,
                                'number_in_procedure': 0
                            })
                        except:
                            pass
                        var_pool = []
                        procedure_context_flag = False

                splitted_line = split_by_separator(remaining_line)
        else:
#             String handle
            append_consumable(segment['text'], 'string')
            for index, constant in enumerate(constants):
                if constant['value'] == segment['text']:
                    break
            tokens_chain.append([
                'C',
                index,
                constant['value'],
                segment['line']
            ])
            kind_suffix = 'C' + str(index)
            print(Fore.BLACK + '\"' + segment['text'] + '\"', Fore.RED + 'STRING', Fore.WHITE + 'by formatter' + Style.RESET_ALL + ' ' + Back.WHITE + 'line #' + str(segment['line']) + Style.RESET_ALL)
            
    return tokens_chain


# In[12]:


constants = []
identifiers = []    

token_chain = to_token_analyze('./pas/program.pas')

data = {
            'chain': tokens_chain,
            'tables': {
                'service_words': service_words,
                'operations': operations,
                'separators': separators,
                'constants': constants,
                'identifiers': identifiers
            }
        }

# print(data)
# print(chain)
with open('./results/lab1.json', 'w') as outfile:
    json.dump(data, outfile)


# In[ ]:





# In[38]:


if tokens_chain:
    for word in tokens_chain:
#         print(word[0] + str(word[1]), end=' ')
        print(word, end=' ')
    # print(tokens_chain)
    print()
    print()

    for i in identifiers:
        print(Fore.RED + i['name'], Fore.GREEN + i['type'])
    print()

    for const in constants:
        if const['type'] == 'string':
            print(Fore.BLUE + '\'' + const['value'] + '\'', Fore.GREEN + const['type'])
        else:
            print(Fore.BLUE + const['value'], Fore.GREEN + const['type'])
    print(Style.RESET_ALL, end='')
else:
    print(tokens_chain)


# In[ ]:





# In[ ]:





# In[ ]:




