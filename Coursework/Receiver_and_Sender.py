from enum import Enum
from numpy import random
import numpy as np

def rand_is_corrupted(p):
    return random.rand() < p

class Package:
    def __init__(self, sequence, message, is_corrupted, point):
        self.sequence = sequence
        self.message = message
        self.is_corrupted = is_corrupted
        self.point = point

class Message(Enum):
    ACK = 0
    NAK = 1

class Transmitter:
    def __init__(self, sender_queue, receiver_queue):
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue

    def get_sender(self):
        if self.sender_queue.empty():
            return None
        return self.sender_queue.get()

    def get_receiver(self):
        if self.receiver_queue.empty():
            return None
        return self.receiver_queue.get()

    def send_receiver(self, msg):
        self.receiver_queue.put(msg)

    def send_sender(self, msg):
        self.sender_queue.put(msg)


class Result:
    def __init__(self):
        self.points = []

    def addPoint(self, point):
        self.points.append(point)

    def getPoint(self, point):
        return self.points

class Receiver:
    def __init__(self, transmitter, protocol, window_size=None, print_comments=False):
        self.transmitter = transmitter
        self.protocol = protocol #0 - Go back N; 1 - selective repeat
        self.window_size = window_size
        self.print_comments = print_comments
        self.total_received = 0
        self.total_sent_ack = 0
        self.points = []
        if self.print_comments:
            print("Receiver created")

    def getData(self):
        return self.points

    def getTotalReceived(self):
        return self.total_received

    def receive(self, num_packages, arr):
        if self.protocol == 0:
            return self.receive_go_back_n(num_packages, arr)
        elif self.protocol == 1:
            return self.receive_selective_repeat(num_packages, arr)

    def receive_go_back_n(self, num_packages, arr):
        while True:
            frame = self.transmitter.get_receiver()
            if frame is None or frame.sequence != self.total_received:
                continue
            if not frame.is_corrupted:
                arr.append(frame.point)
                self.total_received += 1
                if self.print_comments:
                    print("Receiver: Received package with number %d" % frame.sequence)

                self.transmitter.send_sender(Package(frame.sequence, Message.ACK, False, frame.point))
                self.total_sent_ack += 1
                if self.print_comments:
                    print("Receiver: Sent ack for package with number %d" % frame.sequence)
                if self.total_sent_ack == num_packages:
                    if self.print_comments:
                        print("Receiver: finished")
                    return
            else:
                self.transmitter.send_sender(Package(frame.sequence, Message.NAK, False, frame.point))
                if self.print_comments:
                    print("Receiver: Sent nak for package with number %d" % frame.sequence)

    def receive_selective_repeat(self, num_packages, arr):
        buffer = []
        while True:
            package = self.transmitter.get_receiver()
            if package is None:
                continue
            if self.total_received == package.sequence:
                if package.is_corrupted:
                    self.transmitter.send_sender(Package(package.sequence, Message.NAK, False))
                    if self.print_comments:
                        print("Receiver: Sent nak for package with number %d" % package.sequence)
                    continue
                arr.append(package.point)
                self.total_received += 1
                if self.print_comments:
                    print("Receiver: Received package with number %d" % package.sequence)

                self.transmitter.send_sender(Package(package.sequence, Message.ACK, False, package.point))
                self.total_sent_ack += 1
                if self.print_comments:
                    print("Receiver: Sent ack for package with number %d" % package.sequence)

                while len(buffer):
                    if buffer[0].is_corrupted:
                        self.transmitter.send_sender(Package(buffer[0].sequence, Message.NAK, False))
                        if self.print_comments:
                            print("Receiver: Sent nak for package with number %d" % buffer[0].sequence)
                        del buffer[0]
                        break
                    self.total_received += 1
                    if self.print_comments:
                        print("Receiver: Received package with number %d" % buffer[0].sequence)
                    self.transmitter.send_sender(Package(buffer[0].sequence, Message.ACK, False))
                    self.total_sent_ack += 1
                    if self.print_comments:
                        print("Receiver: Sent ack for package with number %d" % buffer[0].sequence)
                    del buffer[0]

                if self.total_sent_ack == num_packages:
                    if self.print_comments:
                        print("Receiver: finished")
                    return
            else:
                buffer.append(package)


class Sender:
    def __init__(self, transmitter, protocol, window_size, print_comments=False):
        self.transmitter = transmitter
        self.protocol = protocol #0 - Go back N; 1 - selective repeat
        self.window_size = window_size
        self.print_comments = print_comments
        self.total_sent = 0
        self.total_received_ack = 0
        if print_comments:
            print("Sender created")

    def send(self, num_packages, p, points):
        window = []
        while True:
            if len(window) < self.window_size and self.total_sent < num_packages:
                package = Package(self.total_sent, None, rand_is_corrupted(p), points[self.total_sent])
                self.transmitter.send_receiver(package)
                window.append(package)
                self.total_sent += 1
                if self.print_comments:
                    print("Sender: Package № %d sent to receiver, corruption = %r" %
                          (package.sequence, package.is_corrupted))

            ack = self.transmitter.get_sender()
            if ack is not None:
                if ack.message == Message.ACK:
                    self.total_received_ack += 1
                    del window[0]
                    if self.print_comments:
                        print("Sender: Package № %d received" % ack.sequence)
                    if self.total_received_ack == num_packages:
                        if self.print_comments:
                            print("Sender: finished")
                        return
                elif ack.message == Message.NAK:
                    if self.protocol == 0:
                        self.go_back_n(window, p)
                    elif self.protocol == 1:
                        self.selective_repeat(window, ack, p)

    def go_back_n(self, window, p):
        for entry in window:
            entry.is_corrupted = rand_is_corrupted(p)
            self.transmitter.send_receiver(entry)
            if self.print_comments:
                print("Sender: Package № %d sent to receiver, corruption = %r" %
                      (entry.sequence, entry.is_corrupted))

    def selective_repeat(self, window, package, p):
        result = window[package.sequence - self.total_received_ack]
        result.is_corrupted = rand_is_corrupted(p)
        self.transmitter.send_receiver(result)
        if self.print_comments:
            print("Sender: Package № %d sent to receiver, corruption = %r" %
                  (result.sequence, result.is_corrupted))