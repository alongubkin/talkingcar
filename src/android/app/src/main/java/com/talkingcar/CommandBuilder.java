package com.talkingcar;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class CommandBuilder {
    private static final int MAGIC = 0xDEADBEEF;

    private static final short COMMAND_TYPE_GAS = 0;
    private static final short COMMAND_TYPE_BRAKE = 1;
    private static final short COMMAND_TYPE_SET_DIRECTION = 2;

    public byte[] brake() {
        ByteBuffer buffer = ByteBuffer.allocate(6);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        // Header
        buffer.putInt(MAGIC);
        buffer.putShort(COMMAND_TYPE_BRAKE);

        return buffer.array();
    }

    public byte[] gas(Gear gear) {
        ByteBuffer buffer = ByteBuffer.allocate(8);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        // Header
        buffer.putInt(MAGIC);
        buffer.putShort(COMMAND_TYPE_GAS);

        // Command params
        buffer.putShort((short) gear.getValue());

        return buffer.array();
    }

    public byte[] setDirection(Direction direction) {
        ByteBuffer buffer = ByteBuffer.allocate(8);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        // Header
        buffer.putInt(MAGIC);
        buffer.putShort(COMMAND_TYPE_SET_DIRECTION);

        // Command params
        buffer.putShort((short) direction.getValue());

        return buffer.array();
    }

    public enum Gear {
        INVALID(-1), FORWARD(0), BACKWARD(1);

        private int _value;

        Gear(int value) {
            _value = value;
        }

        public int getValue() {
            return _value;
        }
    }

    public enum Direction {
        INVALID(-1), RIGHT(0), LEFT(1);

        private int _value;

        Direction(int value) {
            _value = value;
        }

        public int getValue() {
            return _value;
        }
    }
}
