import socket
import struct
import code
import time
from threading import Thread
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.explorers.continuous import NormalExplorer
from pybrain.rl.environments.environment import Environment

MAGIC = 0xDEADBEEF

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

	def __str__(self):
		return "Gas: " + str(self._gear)

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

	def __str__(self):
		return "Set Direction: " + str(self._direction)

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

# class CarEnvironment(Environment):
#
# 	# The number of action values the environment accepts
# 	indim = 7
#
# 	# The number of sensor values the environment produces

def send(client, command):
	message = command.serialize()
	print "Sending", str(command)

	client.send(message)
	time.sleep(1)

def learn(client):
	# av_table = ActionValueTable(4, 7)
	#
	# learner = Q()
	# learner._setExplorer(NormalExplorer(1.0))
	# agent = LearningAgent(av_table, learner)

	data = ""
	struct_size = struct.calcsize(CAR_OUTPUT_FORMAT)


	#send(client, SetDirectionCommand(None))
	send(client, BrakeCommand())

	raw_input("Start")


	send(client, GasCommand("forward"))
	is_forward = True


	while True:
		data += client.recv(struct_size)
		if len(data) < struct_size:
			continue
		else:
			unpacked = struct.unpack(CAR_OUTPUT_FORMAT, data[0:struct_size])
			data = data[struct_size:]

			if unpacked[0] != 0x12345678:
				continue

			car_state = CarState(*unpacked[1:])
			print is_forward, car_state


			# if car_state.current > 450:
			# 	if is_forward:
			# 		send(client, GasCommand("backward"))
			# 		is_forward = False
			# 	else:
			# 		send(client, GasCommand("forward"))
			# 		is_forward = True

			if is_forward:
				if car_state.direction_forward < 100:
					send(client, BrakeCommand())

					if car_state.direction_right > car_state.direction_left:
						send(client, SetDirectionCommand("right"))
					else:
						send(client, SetDirectionCommand("left"))

					send(client, GasCommand("forward"))
				else:
					send(client, SetDirectionCommand(None))



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
