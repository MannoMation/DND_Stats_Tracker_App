# From Computer to Devices:
# A         Stay alive
# I         All devices show their ID
# S         Set device data
# U         Update device data
# C         Clears all leds
# M         Modifies a led

# From Devices to Computer:
# D         Device IDs
# T         Update data

import threading
import time

import DNDHealthTracker


def Init(device):
    global arduino
    arduino = device

    if IsConnected():
        interrupt_thread = threading.Thread(target=serial_interrupt_handler, args=(arduino,))
        interrupt_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
        interrupt_thread.start()

        write_thread = threading.Thread(target=write_messages, args=(arduino,))
        write_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
        write_thread.start()


timeOffset = time.time()
def WriteMessage(message):
    if IsConnected():
        writeMessages.append((message + '\n').encode())


def WriteMessageWithData(code, data):
    if IsConnected():
        message = ""
        message += code

        for d in data:
            message += "," + str(d)

        writeMessages.append((message + ',\n').encode())
        #print(message)


def ReadMessage():
    if IsConnected():
        return arduino.readline().decode('utf-8')
    else:
        return None


def IsConnected():
    return arduino is not None


def write_messages(ser):
    lastTimeMsgSent = time.time()

    while True:
        if len(writeMessages) > 0:
            ser.write(writeMessages[0])
            writeMessages.remove(writeMessages[0])
            lastTimeMsgSent = time.time()
            time.sleep(0.05)
        else:
            if time.time() - lastTimeMsgSent > 5:
                writeMessages.append("A\n".encode())


def serial_interrupt_handler(ser):
    while True:
        if ser.in_waiting > 0:
            read = arduino.readline().decode('utf-8')
            if len(read) > 0:
                print(read)

                if read[0] == 'T':
                    DNDHealthTracker.UpdateCharacterData(read)
                else:
                    messages.append((read, time.time()))

        if len(messages) > 0:
            if time.time() - messages[0][1] > 5:
                messages.remove(messages[0])


def GetMessage(code):
    for m in messages:
        print(m)
        if m[0][0] == code:
            messages.remove(m)
            return m[0]

    return None


arduino = None
messages = []
writeMessages = []
