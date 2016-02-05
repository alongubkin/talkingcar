import socket
import struct
import code
import time
from threading import Thread
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.explorers.continuous import NormalExplorer
from pybrain.rl.environments.environment import Environment
from pybrain.rl.experiments import ContinuousExperiment
from pybrain.rl.environments.task import Task
from pybrain.rl.learners import Q
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased.interface import ActionValueNetwork
from pybrain.rl.learners.valuebased import NFQ
from pybrain.rl.learners.directsearch.reinforce import Reinforce
from pybrain.rl.explorers import EpsilonGreedyExplorer

MAGIC = 0xDEADBEEF
CAR_OUTPUT_MAGIC = 0x12345678

COMMAND_TYPE_GAS = 0
COMMAND_TYPE_BRAKE = 1
COMMAND_TYPE_SET_DIRECTION = 2

GEAR_INVALID = -1
GEAR_FORWARD = 0
GEAR_BACKWARD = 1

DIRECTION_INVALID = -1
DIRECTION_RIGHT = 0
DIRECTION_LEFT = 1

CAR_OUTPUT_FORMAT = "IffffI"

class Command(object):
	def _get_type(self):
		raise NotImplementedError()

	def serialize(self):
		return struct.pack("Ih", MAGIC, self._get_type())

class BrakeCommand(Command):
	def _get_type(self):
		return COMMAND_TYPE_BRAKE

class GasCommand(Command):
	def __init__(self, gear):
		self._gear = gear

	def _get_type(self):
		return COMMAND_TYPE_GAS

	def _serialize_gear(self, gear):
		if gear == "forward":
			return GEAR_FORWARD
		elif gear == "backward":
			return GEAR_BACKWARD

		return GEAR_INVALID

	def serialize(self):
		params = struct.pack("h", self._serialize_gear(self._gear))
		return super(GasCommand, self).serialize() + params

class SetDirectionCommand(Command):
	def __init__(self, direction):
		self._direction = direction

	def _get_type(self):
		return COMMAND_TYPE_SET_DIRECTION

	def _serialize_direction(self, direction):
		if direction == "right":
			return DIRECTION_RIGHT
		elif direction == "left":
			return DIRECTION_LEFT

		return DIRECTION_INVALID

	def serialize(self):
		params = struct.pack("h", self._serialize_direction(self._direction))
		return super(SetDirectionCommand, self).serialize() + params

class CarState(object):
	def __init__(self, direction_forward, direction_backward, direction_right,
					   direction_left, current):
		self.direction_forward = direction_forward
		self.direction_backward = direction_backward
		self.direction_right = direction_right
		self.direction_left = direction_left
		self.current = current

	def __str__(self):
		return "Forward: {0:.2f}cm, Backward: {1:.2f}cm, Right: {2:.2f}cm, Left: {3:.2f}cm, Current: {4}"\
			.format(self.direction_forward, self.direction_backward, self.direction_right, self.direction_left, self.current)

def send(client, command):
	message = command.serialize()
	print ' '.join(hex(ord(x)) for x in message)

	client.send(message)

class CarEnvironment(Environment):
	def __init__(self, client):
		super(Environment, self).__init__()
		self._data = ""
		self._client = client
		self._struct_size = struct.calcsize(CAR_OUTPUT_FORMAT)
		self._max_action = 0
		self._min_action = 0
		self.current = 0

	def getSensors(self):
		while len(self._data) < self._struct_size:
			self._data += self._client.recv(self._struct_size)

		unpacked = struct.unpack(CAR_OUTPUT_FORMAT,
								 self._data[0:self._struct_size])
		self._data = self._data[self._struct_size:]

		if unpacked[0] != CAR_OUTPUT_MAGIC:
			return self.getSensors()

		car_state = CarState(*unpacked[1:])
		print car_state

		self.current = car_state.current

		return [car_state.direction_forward, car_state.direction_backward,
				car_state.direction_right, car_state.direction_left]

	def performAction(self, action):
		action = int(action)

		# if action == -2: # Backward Right
		# 	send(self._client, GasCommand("backward"))
		# 	send(self._client, SetDirectionCommand("right"))
		# elif action == -1: # Backward Left
		# 	send(self._client, GasCommand("backward"))
		# 	send(self._client, SetDirectionCommand("left"))
		# elif action == 0: # Backward None
		# 	send(self._client, GasCommand("backward"))
		# 	send(self._client, SetDirectionCommand(None))
		# elif action == 1: # Forward Right
		# 	send(self._client, GasCommand("forward"))
		# 	send(self._client, SetDirectionCommand("right"))
		# elif action == 2: # Forward
		# 	send(self._client, GasCommand("forward"))
		# 	send(self._client, SetDirectionCommand(None))
		# elif action == 3: # Forward Left
		# 	send(self._client, GasCommand("forward"))
		# 	send(self._client, SetDirectionCommand("left"))

class CarTask(Task):
	def __init__(self, environment):
		self._environment = environment

	def performAction(self, action):
		self._environment.performAction(action)

	def getObservation(self):
		return self._environment.getSensors()

	def getReward(self):
		if self._environment.current > 100:
			return [0,]
		else:
			return [1,]

def learn(client):
	av_table = ActionValueNetwork(4, 1)

	learner = Reinforce()
	agent = LearningAgent(av_table, learner)

	env = CarEnvironment(client)
	task = CarTask(env)

	experiment = ContinuousExperiment(task, agent)

	while True:
		experiment.doInteractionsAndLearn(1)
		agent.learn()

def main():
	client = socket.socket()
	client.connect(("192.168.4.1", 8763))

	def gas(gear):
		send(client, GasCommand(gear))

	def brake():
		send(client, BrakeCommand())

	def direction(direction):
		send(client, SetDirectionCommand(direction))

	Thread(target=learn, args=(client,)).start()
	code.interact(local=dict(globals(), **locals()))

if __name__ == '__main__':
	main()
