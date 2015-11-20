import socket
import struct
import code

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


def main():
	client = socket.socket()
	client.connect(("192.168.4.1", 8763))

	def send(command):
		message = command.serialize()
		print ' '.join(hex(ord(x)) for x in message)

		client.send(message)

	def gas(gear):
		send(GasCommand(gear))

	def brake():
		send(BrakeCommand())

	def direction(direction):
		send(SetDirectionCommand(direction))

	code.interact(local=dict(globals(), **locals()))

if __name__ == '__main__':
	main()