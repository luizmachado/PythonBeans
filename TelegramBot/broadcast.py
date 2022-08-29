import zmq
import sys

kwargs = dict(x.split('=', 1) for x in sys.argv[1:])

context = zmq.Context()

print('Conectando no servidor ZMQ...')
socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

socket.send_string(f'{kwargs["msg"]}')

