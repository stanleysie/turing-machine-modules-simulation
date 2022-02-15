from pprint import pprint

class TuringMachine:
	def __init__(self):
		self.Q = []
		self.S = []
		self.modules = []
		self.accept = None
		self.reject = None
		self.cond = False
		self.input_string = None
		self.pointer = None
		self.debug = False


	def set_input_string(self, input_string):
		self.input_string = input_string
		self.pointer = 0
		if not self.debug:
			print('\n=== INITIAL ===')
			self.display_string(input_string)


	def initialize_turing(self):
		self.Q = []
		self.S = []
		self.accept = None
		self.reject = None


	def parse(self, commands):
		commands = commands.split(' ')
		direction = commands[0]
		transitions = []
		memory = []
		for i in commands[1:]:
			t = i[1:-1]
			t = t.split(',')
			mem = t[0].split('/')
			transitions.append((mem[0].strip(), t[1].strip()))
			memory.append((mem[0].strip(), mem[1].strip()))
		return direction, transitions, memory


	def add_state(self, index, direction=None, transitions=[], memory=[]):
		state = { 'direction': direction, 'index': index, 'next': {}, 'memory': {} }
		for t in transitions:
			state['next'][t[0]] = t[1]
			if not t[0] in self.S:
				self.S.append(t[0])
		for m in memory:
			state['memory'][m[0]] = m[1]
		self.Q.append(state)


	def process_commands(self, commands):
		for i in range(len(commands)):
			if commands[i] == 'accept':
				self.add_state(i+1)
				self.accept = i+1
			elif commands[i] == 'reject':
				self.add_state(i+1)
				self.reject = i+1
			else:
				direction, transitions, memory = self.parse(commands[i])
				self.add_state(i+1, direction, transitions, memory)


	def run_turing(self, string, mult=False):
		state = self.Q[0]

		if self.debug:
			print(f'Initial String: {string}')

		if state['direction'] == 'right':
			self.pointer += 1
		elif state['direction'] == 'left':
			self.pointer -= 1
		
		idx = self.pointer

		while True:
			if state['index'] == self.accept:
				self.cond = True
				break
			elif state['index'] == self.reject:
				self.cond = False
				break

			current = string[idx]

			if current in state['memory'].keys():
				string = [s for s in string]
				string[idx] = state['memory'][current]
				string = ''.join(string)

			next_state = state['next'][current]

			if self.debug and int(next_state) != int(state['index']):
				print(f'State: {state["index"]}')
				print(f'Direction: {state["direction"]}')
				print(f'Current Pointer: {self.pointer}')
				print(f'Next State: {next_state}')
				print(string)
				print(f'{" "*self.pointer}^', end='\n==========================\n')

			state = self.Q[int(next_state)-1]

			if state['direction'] == 'right':
				idx += 1
				self.pointer += 1
			elif state['direction'] == 'left':
				idx -= 1
				self.pointer -= 1

		if not self.debug and not mult:
			self.display_string(string)

		return string


	def add_module(self, module):
		if 'const' in module:
			self.modules.append(('next', self.constant, int(module[1])))
		elif 'shL' in module: 
			self.modules.append(('next', self.shift_left, int(module[1])))
		elif 'shR' in module: 
			self.modules.append(('next', self.shift_right, int(module[1])))
		elif 'copy' in module:
			self.modules.append(('next', self.copy, int(module[1])))
		elif 'move' in module:
			self.modules.append(('next', self.move, int(module[1]), int(module[2])))
		elif 'swap' in module:
			self.modules.append(('next', self.swap))
		elif 'add' in module:
			self.modules.append(('next', self.add))
		elif 'monus' in module:
			self.modules.append(('next', self.monus))
		elif 'mult' in module:
			self.modules.append(('next', self.multiply))
		elif 'divide' in module:
			self.modules.append(('next', self.divide))
		elif 'ifGT' in module:
			self.modules.append(('goto', self.greater_than, int(module[1])))
		elif 'ifGE' in module:
			self.modules.append(('goto', self.greater_than_equal, int(module[1])))
		elif 'ifLT' in module:
			self.modules.append(('goto', self.less_than, int(module[1])))
		elif 'ifLE' in module:
			self.modules.append(('goto', self.less_than_equal, int(module[1])))
		elif 'ifEQ' in module:
			self.modules.append(('goto', self.equal, int(module[1])))
		elif 'ifNE' in module:
			self.modules.append(('goto', self.not_equal, int(module[1])))
		elif 'goto' in module:
			self.modules.append(('goto', self.go_to, int(module[1])))
		elif 'halt' in module:
			self.modules.append(('halt', ))


	def run_modules(self):
		m = self.modules[0]
		idx = 0

		while True:
			if 'halt' in m:
				break
			elif 'next' in m:
				if len(m) == 2:
					_, module = m
					module()
					idx += 1
				elif len(m) == 3:
					_, module, x = m
					module(x)
					idx += 1
				elif len(m) == 4:
					_, module, x, y = m
					module(x, y)
					idx += 1
			elif 'goto' in m:
				_, module, x = m
				module(x)
				if self.cond:
					idx = x-1
				else:
					idx += 1

			m = self.modules[idx]

			# remove trailing '#'s
			substrings = self.input_string.split('#')
			self.input_string = '#'
			for s in substrings:
				if s != '':
					self.input_string += s + '#'


	def display_string(self, string):
		print(string)
		print(f'{" "*self.pointer}^')


	#############
	#  MODULES  #
	#############

	def constant(self, k):
		print(f'\n=== CONSTANT: {k} ===')
		self.initialize_turing()
		self.input_string += '#'*(2*k)
		
		commands = []
		for i in range(k):
			commands.append(f'right (#/1,{i+2})')
		commands += [f'left (1/1,{k+1}) (#/#,{k+2})', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def shift_left(self, k):
		print(f'\n=== SHIFT LEFT: {k} ===')
		self.initialize_turing()

		commands = []
		for i in range(k):
			commands.append(f'left (1/1,{i+1}) (#/#,{i+2})')
		commands.append('accept')
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def shift_right(self, k):
		print(f'\n=== SHIFT RIGHT: {k} ===')
		self.initialize_turing()
		self.input_string += '#'*k

		commands = []
		for i in range(k):
			commands.append(f'right (1/1,{i+1}) (#/#,{i+2})')
		commands.append('accept')
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def copy(self, k):
		print(f'\n=== COPY: {k} ===')
		self.initialize_turing()
		substrings = self.input_string[:self.pointer].split('#')
		substrings = [s for s in substrings if s != '']
		substrings = ''.join(substrings[len(substrings)-k:])
		self.input_string += '#'*(len(substrings)+1)
			
		commands = []
		for i in range(k):
			commands.append(f'left (1/1,{i+1}) (#/#,{i+2})')
		commands.append(f'right (1/x,{len(commands)+2}) (#/#,{3*k+4})')
		for i in range(len(commands), len(commands)+k):
			commands.append(f'right (1/1,{i+1}) (#/#,{i+2})')
		commands.append(f'right (1/1,{len(commands)+1}) (#/1,{len(commands)+2})')
		for i in range(len(commands), len(commands)+k):
			commands.append(f'left (1/1,{i+1}) (#/#,{i+2})')
		commands.append(f'left (1/1,{len(commands)+1}) (x/1,{k+1})')
		for i in range(len(commands), len(commands)+k):
			commands.append(f'right (1/1,{len(commands)+1}) (#/#,{len(commands)+2})')
		commands.append('accept')
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def move(self, j, k, mult=False):
		if not mult:
			print(f'\n=== MOVE: {j},{k} ===')
		self.initialize_turing()

		commands = []
		if k == 0:
			for i in range(j):
				commands.append(f'left (1/#,{i+1}) (#/#,{i+2})')
		else:
			for i in range(k-1):
				commands.append(f'right (1/1,{len(commands)+1}) (#/#,{len(commands)+2})')
			commands.append(f'right (1/1,{len(commands)+1}) (#/x,{len(commands)+2})')
			for i in range(k):
				commands.append(f'left (1/1,{len(commands)+1}) (#/#,{len(commands)+2})')
			for i in range(j-1):
				commands.append(f'left (1/x,{len(commands)+1}) (#/x,{len(commands)+2})')
			commands.append(f'left (1/x,{len(commands)+1}) (#/#,{len(commands)+2})')
			checkpoint = len(commands)+1
			commands.append(f'right (x/x,{len(commands)+1}) (#/#,{len(commands)+2})')
			commands.append(f'right (a/a,{len(commands)+1}) (1/a,{len(commands)+2}) (#/a,{len(commands)+5}) (x/#,{len(commands)+8})')
			commands.append(f'left (a/a,{len(commands)+1}) (#/#,{len(commands)+2}) (1/1,{len(commands)+3})')
			commands.append(f'left (x/x,{len(commands)+1}) (#/#,{len(commands)+2}) (1/1,{len(commands)+2})')
			commands.append(f'right (x/1,{checkpoint}) (#/1,{checkpoint+1}) (a/1,{checkpoint+1})')
			commands.append(f'left (a/a,{len(commands)+1}) (#/#,{len(commands)+2})')
			commands.append(f'left (x/x,{len(commands)+1}) (#/#,{len(commands)+2}) (1/1,{len(commands)+2})')
			commands.append(f'right (x/#,{checkpoint})')
			commands.append(f'left (a/#,{len(commands)+1}) (#/#,{len(commands)+2}) (1/1,{len(commands)+2})')
			commands.append(f'left (x/#,{len(commands)+1}) (1/1,{len(commands)+2}) (#/#,{len(commands)+2})')
			for i in range(k):
				commands.append(f'left (1/1,{len(commands)+1}) (#/#,{len(commands)+2})')
		commands.append('accept')
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def swap(self):
		print('\n=== SWAP ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,7)', 'right (1/1,2) (#/#,3)', 'right (1/1,3) (x/x,3) (#/#,4)',
					'left (1/x,5) (x/x,4) (#/1,15)', 'left (1/1,5) (#/#,6)', 'left (1/1,6) (x/1,1)',
					'right (x/1,12) (1/1,8)', 'left (#/1,9)', 'right (1/1,9) (x/x,10) (#/#,10)',
					'left (1/#,11)', 'right (x/1,11) (#/#,13)', 'right (x/1,12) (#/#,13)',
					'left (1/1,13) (#/#,14)', 'left (1/1,14) (#/#,17)', 'right (1/1,15) (x/1,15) (#/#,16)', 
					'left (1/1,16) (x/#,16) (#/#,17)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def add(self):
		print('\n=== ADDITION ===')
		self.initialize_turing()

		commands = ['right (1/1,1) (#/1,2)', 'right (1/1,2) (#/#,3)', 'left (1/#,4)',
					'left (1/1,4) (#/#,5)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def monus(self):
		print('\n=== MONUS ===')
		self.initialize_turing()

		commands = ['right (1/1,1) (#/#,2)', 'right (1/1,2) (#/#,3)', 'left (1/#,4) (#/#,7)',
					'left (1/1,4) (#/#,5)', 'left (x/x,5) (1/x,6)', 'right (x/x,6) (#/#,2)',
					'left (x/#,7) (1/1,7) (#/#,8)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def multiply(self):
		print('\n=== MULTIPLICATION ===')
		self.initialize_turing()
		substring = self.input_string[self.pointer:].split('#')
		self.input_string += '#'*(len(substring[1])*len(substring[2])+2)

		commands = ['right (1/x,2) (#/#,10)', 'right (1/1,2) (#/#,3)', 'right (a/a,3) (1/a,4) (#/#,8)',
					'right (1/1,4) (#/#,5)', 'right (1/1,5) (#/1,6)', 'left (1/1,6) (#/#,7)',
					'left (1/1,7) (a/a,3)', 'left (a/1,8) (#/#,9)', 'left (1/1,9) (x/1,1)',
					'right (1/1,10) (#/#,11)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string, True)
		self.move(2, 1, True)


	def divide(self):
		print('\n=== DIVISION ===')
		self.initialize_turing()
		self.input_string += '#'*(self.input_string.count('1'))

		commands = ['right (1/1,1) (#/#,2)', 'right (1/x,3) (#/#,7)', 'left (1/1,3) (#/#,4)',
					'left (1/1,4) (#/#,5) (x/1,5)', 'right (#/#,6) (1/x,10)', 'right (1/1,6) (x/1,6) (#/#,12)',
					'right (1/1,7) (#/1,8)', 'left (1/1,8) (#/#,9)', 'left (1/1,9) (#/#,2)',
					'right (1/1,10) (#/#,11)', 'right (1/1,11) (x/1,2)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string, True)
		self.move(2, 1, True)


	def greater_than(self, state):
		print(f'\n=== GREATER THAN: {state} ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,11)', 'right (1/1,2) (#/#,3)', 'right (x/x,3) (1/x,4) (#/#,6)',
					'left (x/x,4) (#/#,5)', 'left (1/1,5) (x/x,1)', 'left (x/#,6) (#/#,7)',
					'left (1/#,7) (x/#,7) (#/#,10)', 'left (#/#,8) (x/#,9)', 'left (x/#,9) (#/#,15)',
					'accept', 'right (x/#,11) (1/#,12) (#/#,8)', 'right (1/#,12) (#/#,13)',
					'left (#/#,13) (x/#,14)', 'left (x/#,14) (#/#,15)', 'reject']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def greater_than_equal(self, state):
		print(f'\n=== GREATER THAN OR EQUAL: {state} ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,11)', 'right (1/1,2) (#/#,3)', 'right (x/x,3) (1/x,4) (#/#,6)',
					'left (x/x,4) (#/#,5)', 'left (1/1,5) (x/x,1)', 'left (x/#,6) (#/#,7)',
					'left (1/#,7) (x/#,7) (#/#,10)', 'left (#/#,8) (x/#,9)', 'left (x/#,9) (#/#,10)',
					'accept', 'right (x/#,11) (1/#,12) (#/#,8)', 'right (1/#,12) (#/#,13)',
					'left (#/#,13) (x/#,14)', 'left (x/#,14) (#/#,15)', 'reject']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def less_than(self, state):
		print(f'\n=== LESS THAN: {state} ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,11)', 'right (1/1,2) (#/#,3)', 'right (x/x,3) (1/x,4) (#/#,6)',
					'left (x/x,4) (#/#,5)', 'left (1/1,5) (x/x,1)', 'left (x/#,6) (#/#,7)',
					'left (1/#,7) (x/#,7) (#/#,10)', 'left (#/#,8) (x/#,9)', 'left (x/#,9) (#/#,10)',
					'reject', 'right (x/#,11) (1/#,12) (#/#,8)', 'right (1/#,12) (#/#,13)',
					'left (#/#,13) (x/#,14)', 'left (x/#,14) (#/#,15)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def less_than_equal(self, state):
		print(f'\n=== LESS THAN OR EQUAL: {state} ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,11)', 'right (1/1,2) (#/#,3)', 'right (x/x,3) (1/x,4) (#/#,6)',
					'left (x/x,4) (#/#,5)', 'left (1/1,5) (x/x,1)', 'left (x/#,6) (#/#,7)',
					'left (1/#,7) (x/#,7) (#/#,10)', 'left (#/#,8) (x/#,9)', 'left (x/#,9) (#/#,15)',
					'reject', 'right (x/#,11) (1/#,12) (#/#,8)', 'right (1/#,12) (#/#,13)',
					'left (#/#,13) (x/#,14)', 'left (x/#,14) (#/#,15)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def equal(self, state):
		print(f'\n=== EQUAL: {state} ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,6)', 'right (1/1,2) (#/#,3)','right (x/x,3) (1/x,4) (#/#,13)',
					'left (x/x,4) (#/#,5)', 'left (1/1,5) (x/x,1)', 'right (x/#,6) (1/#,10) (#/#,7)', 
					'left (#/#,7) (x/#,8)', 'left (x/#,8) (#/#,9)','accept', 'right (1/#,10) (#/#,11)',
					'left (#/#,11) (x/#,12)', 'left (x/#,12) (#/#,15)', 'left (x/#,13) (#/#,14)',
					'left (1/#,14) (x/#,14) (#/#,15)', 'reject']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def not_equal(self, state):
		print(f'\n=== NOT EQUAL: {state} ===')
		self.initialize_turing()

		commands = ['right (1/x,2) (#/#,6)', 'right (1/1,2) (#/#,3)','right (x/x,3) (1/x,4) (#/#,13)',
					'left (x/x,4) (#/#,5)', 'left (1/1,5) (x/x,1)', 'right (x/#,6) (1/#,10) (#/#,7)', 
					'left (#/#,7) (x/#,8)', 'left (x/#,8) (#/#,9)','reject', 'right (1/#,10) (#/#,11)',
					'left (#/#,11) (x/#,12)', 'left (x/#,12) (#/#,15)', 'left (x/#,13) (#/#,14)',
					'left (1/#,14) (x/#,14) (#/#,15)', 'accept']
		self.process_commands(commands)
		self.input_string = self.run_turing(self.input_string)


	def go_to(self, state):
		print(f'\n=== GOTO: {state} ===')
		self.display_string(self.input_string)


TM = TuringMachine()

try:
    # load from a file
    with open('sort_3_numbers.txt') as f:
        lines = f.readlines()
        print('=== PROGRAM ===')
        for i in range(len(lines)):
        	print(f'{i+1}) {lines[i][:-1].split(" ")[1:]}')
        	TM.add_module(lines[i][:-1].split(' ')[1:])
except FileNotFoundError as e:
    print('No test file found.', end='\n\n')
    # input program manually
    print('Enter program string:')
    i = 0
    while True:
        state = input(f'{i+1}) ')
        if state in ['', '\n']:
        	break
        TM.add_module(state.split(' '))
        i += 1

while True:
	string = input("\nType 'exit' to close\nEnter string: ")
	if string == 'exit':
		break
	else:
		TM.set_input_string(string)
		TM.run_modules()