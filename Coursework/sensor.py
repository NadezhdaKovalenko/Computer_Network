#from screen import Screen
import numpy as np
from Receiver_and_Sender import Receiver, Sender, Transmitter
from multiprocessing import Queue, Process, Manager, Array
from matplotlib import pyplot
import matplotlib.pyplot as plt

class Sensor:
    def __init__(self, imgs, sensor_id):
        self.imgs = imgs
        self.intersections = []
        self.senders = []
        self.transmitters = []
        self.receivers = []
        self.data_from_receiver = []
        self.received_data = {}
        self.received_data_sets = {}
        self.sensor_id = sensor_id

    def setIntersections(self, intersections):
        self.intersections = intersections

    def getIntersections(self):
        return self.intersections

    def getReceivers(self):
        return self.receivers

    def getTransmitters(self):
        return self.transmitters

    def getReceiversAndData(self):
        return self.receivers, self.data_from_receiver

    def setSenderReceiverParametres(self, senders, transmitters, receivers, receivers_data):
        self.senders = senders
        self.transmitters = transmitters
        self.receivers = receivers
        self.data_from_receiver = receivers_data

    def setSenderTransmitter(self, senders, transmitters):
        self.senders = senders
        self.transmitters = transmitters

    def getSenderReceiverParametres(self):
        return self.transmitters, self.senders, self.receivers

    def generateRandPoints(self):
        points_num = len(self.intersections)
        rand_points = []
        for i in range(points_num):
            rand_points.append([np.random.rand(), np.random.rand()])
        return rand_points

    def generateRandPointsArray(self, size_arr):
        rand_points = []
        for i in range(size_arr):
            rand_points.append(np.random.rand())
        return rand_points

    def send_broadcast_intersections(self, corruption_p, receivers, data):
        num_packages = len(self.intersections)  # number of packages
        receivers_num = len(self.transmitters)
        send_data = self.intersections.copy()
        for i in range(receivers_num):
            if self.swindler == True:
                send_data = self.generateRandPoints()
            sender_proc = Process(target=self.senders[i].send, args=(num_packages, corruption_p, send_data))
            receiver_proc = Process(target=receivers[i].receive, args=(num_packages, data[i], ))
            sender_proc.start()
            receiver_proc.start()
            receiver_proc.join()
            sender_proc.join()

    def send_broadcast_set_intersections(self, corruption_p, receivers, data):
        num_packages = len(self.received_data)  # number of packages
        receivers_num = len(self.transmitters)
        send_data = []
        for i in range(1, num_packages + 1):
            send_data.append(self.received_data[i])
        size = len(send_data)
        if self.swindler == True:
            send_data.clear()
            for i in range(size):
                send_data.append(self.generateRandPoints())
        for i in range(receivers_num):
            sender_proc = Process(target=self.senders[i].send, args=(num_packages, corruption_p, send_data))
            receiver_proc = Process(target=receivers[i].receive, args=(num_packages, data[i], ))
            sender_proc.start()
            receiver_proc.start()
            receiver_proc.join()
            sender_proc.join()

    def setReceivedData(self, sensors_num):
        self.received_data = {a: [] for a in range(1, sensors_num + 1)}
        other_sensors_ids = []
        for i in range(1, sensors_num + 1):
            if i != self.sensor_id:
                other_sensors_ids.append(i)

        self.received_data[self.sensor_id] = self.intersections
        for i in range(len(self.receivers)):
            tmp_list = []
            for j in range(len(self.data_from_receiver[i])):
                tmp_list.append(self.data_from_receiver[i][j])
            self.received_data[other_sensors_ids[i]] = tmp_list

    def setReceivedData2(self, sensors_num):
        this_sensor_data = []
        for i in range(1, len(self.received_data) + 1):
            this_sensor_data.append(self.received_data[i])

        self.received_data_sets = {a: [] for a in range(1, sensors_num + 1)}
        other_sensors_ids = []
        for i in range(1, sensors_num + 1):
            if i != self.sensor_id:
                other_sensors_ids.append(i)

        self.received_data_sets[self.sensor_id] = this_sensor_data
        for i in range(len(self.receivers)):
            tmp_list = []
            for j in range(len(self.data_from_receiver[i])):
                tmp_list.append(self.data_from_receiver[i][j])
            self.received_data_sets[other_sensors_ids[i]] = tmp_list

    def makeResultVector(self):
        res_vector = [[], [], [], []]
        size = len(self.received_data_sets)
        for k in range(size):
            tmp_list = []
            for i in range(1, size + 1):
                tmp_list.append(self.received_data_sets[i][k])
            for point in tmp_list:
                if tmp_list.count(point) > 1:
                    res_vector[k] = point
                    break
        return res_vector

    def sendResultVectorToRouter(self, corruption_p, receiver, data):
        res_vector = self.makeResultVector()
        num_packages = len(res_vector)
        sender_proc = Process(target=self.senders[0].send, args=(num_packages, corruption_p, res_vector))
        receiver_proc = Process(target=receiver.receive, args=(num_packages, data))
        sender_proc.start()
        receiver_proc.start()
        receiver_proc.join()
        sender_proc.join()

    def drawOneImg(self, ind):
        plt.figure()
        plt.imshow(self.imgs[ind])
        plt.grid(False)
        plt.show()


def calculateSensorParameters(square_num, screen_centre, screen_height):
    sensor_centre = [0, 0]
    if square_num == 1:
        sensor_centre[0] = screen_centre[0] - screen_height / 4
        sensor_centre[1] = screen_centre[1] - screen_height / 4
    elif square_num == 2:
        sensor_centre[0] = screen_centre[0] - screen_height / 4
        sensor_centre[1] = screen_centre[1] + screen_height / 4
    elif square_num == 3:
        sensor_centre[0] = screen_centre[0] + screen_height / 4
        sensor_centre[1] = screen_centre[1] + screen_height / 4
    elif square_num == 4:
        sensor_centre[0] = screen_centre[0] + screen_height / 4
        sensor_centre[1] = screen_centre[1] - screen_height / 4
    return sensor_centre, screen_height/2


class DesignatedRouter:
    def __init__(self, numCamers, numImgs, imgs):
        self.sensors_num = numCamers
        self.imgs_one_camera = numImgs
        self.sensors = []
        for i in range(numCamers):
            self.sensors.append(Sensor(imgs[i*numImgs:(i+1)*numImgs-1], i+1))

        self.data_from_sensors = []

    def setIntersectionsForSensors(self, intersections_sensor1, intersections_sensor2,
                                   intersections_sensor3, intersections_sensor4, centre_square):
        if len(intersections_sensor1) > 0 or centre_square == 1:
            self.sensor_1.setIntersections(intersections_sensor1)
        if len(intersections_sensor2) > 0 or centre_square == 2:
            self.sensor_2.setIntersections(intersections_sensor2)
        if len(intersections_sensor3) > 0 or centre_square == 3:
            self.sensor_3.setIntersections(intersections_sensor3)
        if len(intersections_sensor4) > 0 or centre_square == 4:
            self.sensor_4.setIntersections(intersections_sensor4)

    def getPoints(self):
        points1 = self.sensor_1.getIntersections()
        points2 = self.sensor_2.getIntersections()
        points3 = self.sensor_3.getIntersections()
        points4 = self.sensor_4.getIntersections()
        return points1 + points2 + points3 + points4

    def setSenderReceiverParametres(self, protocol, window_size, receivers_num, arr_size):
        transmitters_1, transmitters_2, transmitters_3, transmitters_4 = [], [], [], []
        senders_1, senders_2, senders_3, senders_4 = [], [], [], []
        receivers_1, receivers_2, receivers_3, receivers_4 = [], [], [], []
        receivers_data_1, receivers_data_2, receivers_data_3, receivers_data_4 = [], [], [], []
        manager = Manager()
        for i in range(receivers_num):
            transmitters_1.append(Transmitter(Queue(), Queue()))
            transmitters_2.append(Transmitter(Queue(), Queue()))
            transmitters_3.append(Transmitter(Queue(), Queue()))
            transmitters_4.append(Transmitter(Queue(), Queue()))
            receivers_1.append(Receiver(transmitters_1[i], protocol, window_size))
            receivers_2.append(Receiver(transmitters_2[i], protocol, window_size))
            receivers_3.append(Receiver(transmitters_3[i], protocol, window_size))
            receivers_4.append(Receiver(transmitters_4[i], protocol, window_size))
            receivers_data_1.append(manager.list())
            receivers_data_2.append(manager.list())
            receivers_data_3.append(manager.list())
            receivers_data_4.append(manager.list())

        senders_1.append(Sender(transmitters_2[0], protocol, window_size))
        senders_1.append(Sender(transmitters_3[0], protocol, window_size))
        senders_1.append(Sender(transmitters_4[0], protocol, window_size))

        senders_2.append(Sender(transmitters_1[0], protocol, window_size))
        senders_2.append(Sender(transmitters_3[1], protocol, window_size))
        senders_2.append(Sender(transmitters_4[1], protocol, window_size))

        senders_3.append(Sender(transmitters_1[1], protocol, window_size))
        senders_3.append(Sender(transmitters_2[1], protocol, window_size))
        senders_3.append(Sender(transmitters_4[2], protocol, window_size))

        senders_4.append(Sender(transmitters_1[2], protocol, window_size))
        senders_4.append(Sender(transmitters_2[2], protocol, window_size))
        senders_4.append(Sender(transmitters_3[2], protocol, window_size))

        self.sensor_1.setSenderReceiverParametres(senders_1, transmitters_1, receivers_1, receivers_data_1)
        self.sensor_2.setSenderReceiverParametres(senders_2, transmitters_2, receivers_2, receivers_data_2)
        self.sensor_3.setSenderReceiverParametres(senders_3, transmitters_3, receivers_3, receivers_data_3)
        self.sensor_4.setSenderReceiverParametres(senders_4, transmitters_4, receivers_4, receivers_data_4)

    def setSenderReceiverParametres_oneReceaiver(self, protocol, window_size):
        transmitters_1, transmitters_2, transmitters_3, transmitters_4 = [], [], [], []
        senders_1, senders_2, senders_3, senders_4 = [], [], [], []

        transmitters_1.append(Transmitter(Queue(), Queue()))
        transmitters_2.append(Transmitter(Queue(), Queue()))
        transmitters_3.append(Transmitter(Queue(), Queue()))
        transmitters_4.append(Transmitter(Queue(), Queue()))

        senders_1.append(Sender(transmitters_1[0], protocol, window_size))
        senders_2.append(Sender(transmitters_2[0], protocol, window_size))
        senders_3.append(Sender(transmitters_3[0], protocol, window_size))
        senders_4.append(Sender(transmitters_4[0], protocol, window_size))

        self.sensor_1.setSenderTransmitter(senders_1, transmitters_1)
        self.sensor_2.setSenderTransmitter(senders_2, transmitters_2)
        self.sensor_3.setSenderTransmitter(senders_3, transmitters_3)
        self.sensor_4.setSenderTransmitter(senders_4, transmitters_4)

    def processSendRecieveIntersections(self, corruption_p):
        receivers_1, data_1 = self.sensor_1.getReceiversAndData()
        receivers_2, data_2 = self.sensor_2.getReceiversAndData()
        receivers_3, data_3 = self.sensor_3.getReceiversAndData()
        receivers_4, data_4 = self.sensor_4.getReceiversAndData()

        self.sensor_1.send_broadcast_intersections(corruption_p, [receivers_2[0], receivers_3[0], receivers_4[0]],
                                                   [data_2[0], data_3[0], data_4[0]])
        self.sensor_2.send_broadcast_intersections(corruption_p, [receivers_1[0], receivers_3[1], receivers_4[1]],
                                                   [data_1[0], data_3[1], data_4[1]])
        self.sensor_3.send_broadcast_intersections(corruption_p, [receivers_1[1], receivers_2[1], receivers_4[2]],
                                                   [data_1[1], data_2[1], data_4[2]])
        self.sensor_4.send_broadcast_intersections(corruption_p, [receivers_1[2], receivers_2[2], receivers_3[2]],
                                                   [data_1[2], data_2[2], data_3[2]])
        print('Формирование вектора с координатами точек пересечения, полученными от других узлов')
        self.sensor_1.setReceivedData(self.sensors_num)
        self.sensor_2.setReceivedData(self.sensors_num)
        self.sensor_3.setReceivedData(self.sensors_num)
        self.sensor_4.setReceivedData(self.sensors_num)

    def processSendRecieveSets(self, corruption_p):
        receivers_1, data_1 = self.sensor_1.getReceiversAndData()
        receivers_2, data_2 = self.sensor_2.getReceiversAndData()
        receivers_3, data_3 = self.sensor_3.getReceiversAndData()
        receivers_4, data_4 = self.sensor_4.getReceiversAndData()

        self.sensor_1.send_broadcast_set_intersections(corruption_p, [receivers_2[0], receivers_3[0], receivers_4[0]],
                                                       [data_2[0], data_3[0], data_4[0]])
        self.sensor_2.send_broadcast_set_intersections(corruption_p, [receivers_1[0], receivers_3[1], receivers_4[1]],
                                                       [data_1[0], data_3[1], data_4[1]])
        self.sensor_3.send_broadcast_set_intersections(corruption_p, [receivers_1[1], receivers_2[1], receivers_4[2]],
                                                       [data_1[1], data_2[1], data_4[2]])
        self.sensor_4.send_broadcast_set_intersections(corruption_p, [receivers_1[2], receivers_2[2], receivers_3[2]],
                                                       [data_1[2], data_2[2], data_3[2]])
        print('Формирование набора векторов, полученными от других узлов')
        self.sensor_1.setReceivedData2(self.sensors_num)
        self.sensor_2.setReceivedData2(self.sensors_num)
        self.sensor_3.setReceivedData2(self.sensors_num)
        self.sensor_4.setReceivedData2(self.sensors_num)

    def resievePointsFromSensors(self, protocol, window_size, corruption_p):
        receiver_1 = Receiver(self.sensor_1.getTransmitters()[0], protocol, window_size)
        receiver_2 = Receiver(self.sensor_2.getTransmitters()[0], protocol, window_size)
        receiver_3 = Receiver(self.sensor_3.getTransmitters()[0], protocol, window_size)
        receiver_4 = Receiver(self.sensor_4.getTransmitters()[0], protocol, window_size)
        manager = Manager()
        data_1 = manager.list()
        data_2 = manager.list()
        data_3 = manager.list()
        data_4 = manager.list()

        print('Создание результирующего вектора')
        print('Передача результирующего вектора на роутер')
        self.sensor_1.sendResultVectorToRouter(corruption_p, receiver_1, data_1)
        self.sensor_2.sendResultVectorToRouter(corruption_p, receiver_2, data_2)
        self.sensor_3.sendResultVectorToRouter(corruption_p, receiver_3, data_3)
        self.sensor_4.sendResultVectorToRouter(corruption_p, receiver_4, data_4)

        all_vectors = [data_1, data_2, data_3, data_4]

        return all_vectors

    def processGetDataFromSensors(self, protocol, window_size):
        corruption_p = 0
        print('Начало решения Византийской задачи')
        self.setSenderReceiverParametres(protocol, window_size, self.sensors_num - 1, 4)
        print('Рассылка сообщения с координатами точек пересечения всем узлам сети')
        self.processSendRecieveIntersections(corruption_p)
        self.setSenderReceiverParametres(protocol, window_size, self.sensors_num - 1, 12)
        print('Рассылка сообщения с вектором, содержащим координаты точек пересечения, всем узлам сети')
        self.processSendRecieveSets(corruption_p)
        self.setSenderReceiverParametres_oneReceaiver(protocol, window_size)
        self.data_from_sensors = self.resievePointsFromSensors(protocol, window_size, corruption_p)

    def calculateNewCentre(self):
        print('Расчет центра окружности по полученным точкам')
        size = len(self.data_from_sensors)
        points = []
        for i in range(size):
            if len(self.data_from_sensors[0][i]) != 0:
                points.append(self.data_from_sensors[0][i][0])
                points.append(self.data_from_sensors[0][i][1])

        if len(points) <= 2:
            print ('cant calculate new centre')
            return [np.nan, np.nan]

        point1 = points[0]
        point2 = [np.nan, np.nan]
        point3 = [np.nan, np.nan]
        for point in points:
            if point[0] != point1[0] or point[1] != point1[1]:
                point2 = point
        for point in points:
            if ((point[0] != point1[0] or point[1] != point1[1]) and
                    (point[0] != point2[0] or point[1] != point2[1])):
                point3 = point

        if (point2[0] is np.nan) or (point3[0] is np.nan):
            print ('cant calculate new centre')
            return [np.nan, np.nan]

        A = point2[0] - point1[0]
        B = point2[1] - point1[1]
        C = point3[0] - point1[0]
        D = point3[1] - point1[1]
        E = A * (point2[0] + point1[0]) + B * (point2[1] + point1[1])
        F = C * (point3[0] + point1[0]) + D * (point3[1] + point1[1])
        G = 2 * (A * (point3[1] - point2[1]) - B * (point3[0] - point2[0]))
        Cx = (D * E - B * F) / G
        Cy = (A * F - C * E) / G
        centre = [Cx, Cy]
        return centre