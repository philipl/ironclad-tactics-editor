save_pb2.py: save.proto
	protoc --python_out=. save.proto

default: save_pb2.py

clean:
	rm save_pb2.py*
