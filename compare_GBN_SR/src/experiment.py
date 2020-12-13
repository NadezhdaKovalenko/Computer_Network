import connections as con
import time


class Experiment:
    def __init__(
            self,
            protocol_type: str,
            window_size=16,
            lose_prob=0.5,
            transfer_number=-1,
            seconds=-1
    ):
        self.connection = con.PointToPoint(
            protocol_type,
            window_size,
            lose_prob,
            transfer_number=transfer_number,
            seconds=seconds
        )

        self.transfer_number = transfer_number

    def calc_time(self) -> float:
        start_time = time.time()
        self.connection.start_transmission()
        end_time = time.time()
        return end_time - start_time

    def calc_efficiency(self):
        self.connection.start_transmission()
        return self.connection.pack_number[0]
