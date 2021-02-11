from multiprocessing import Pipe


class Channel:
    """
    Two-way channel between agents.
    """
    def __init__(self, pipe):
        self.pipe = pipe


    def send(self, msg):
        self.pipe.send(msg)


    def poll(self, timeout=None):
        return self.pipe.poll(timeout)


    def recv(self):
        return self.pipe.recv()

    
    def close(self):
        return self.pipe.close()


class BaseConnection:
    """
    Connection between two agents: two channels
    for parent and child.
    """
    def __init__(self):
        self.parent, self.child = Pipe()
        self.parent_channel = Channel(self.parent)
        self.child_channel = Channel(self.child)


    def sender(self):
        return self.parent_channel


    def receiver(self):
        return self.child_channel


class Connection(BaseConnection):
    """
    Connection that remembers from-to identifiers
    """
    def __init__(self, from_idx, to_idx):
        super().__init__()
        self.parent_channel.type = 'sender'
        self.child_channel.type = 'receiver'
        self.parent_channel.to_idx = to_idx
        self.child_channel.from_idx = from_idx


class Message:
    def __init__(self, sender_idx=None, recepient_idx=None, data=None):
        self.sender_idx = sender_idx
        self.recepient_idx = recepient_idx
        self.data = data
        
        
    def __repr__(self):
        return f"<#{type(self)} ({self.sender_idx})->({self.recepient_idx})>" # = [{self.data}]>"


class HelloMessage(Message):
    pass


class StartCorrectionMessage(Message):
    pass


class StopCorrectionMessage(Message):
    pass


class AskEnergyMessage(Message):
    pass


class RespondEnergyMessage(Message):
    pass