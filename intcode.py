from collections import deque

def init_intcode_run(arr, pos, phase_setting, dependency_key, queue_dict, first_run, first_producer, consume, produce):
    return IntcodeProgram(arr, pos, phase_setting, dependency_key, queue_dict, first_run, first_producer, consume, produce)

class IntcodeProgram:
    def __init__(self, arr, pos, phase_setting, dependency_key, queue_dict, first_run, first_producer, consume, produce):
        self.phase_setting = phase_setting
        self.first_producer = first_producer
        self.first_run = first_run
        self.dependency_key = dependency_key
        self.consume = consume
        self.produce = produce
        self.queue_dict = queue_dict
        self.relative_base = 0
        self.arr = arr
        self.pos = pos
        done = False
        while not done:
            done = self.intcode_parser(self.arr, self.pos)

    def get_val(self, arr, position, parameter=0):
        try:
            if parameter == 0:
                return arr[arr[position]]
            elif parameter == 1:
                return arr[position]
            else:
                return arr[self.relative_base + arr[position]]
        except IndexError:
            return 0

    def set_val(self, val, arr, position, parameter=0):
            if parameter == 0:
                try:
                    arr[arr[position]] = val
                except IndexError:
                    arr.extend([0] * (arr[position] - len(arr) + 1))
                    arr[arr[position]] = val
            elif parameter == 1:
                try:
                    arr[position] = val
                except IndexError:
                    arr.extend([0] * (position - len(arr) + 1))
                    arr[position] = val
            else:
                try:
                    arr[self.relative_base + arr[position]] = val
                except IndexError:
                    arr.extend([0] * (self.relative_base + arr[position] - len(arr) + 1))
                    arr[self.relative_base + arr[position]] = val

    def intcode_parser(self, arr, pos):
        op = arr[pos]
        parameters = (0, 0, 0)
        if op > 99:
            parameters = ((op // 100) % 10, (op // 1000) % 10, (op // 10000) % 10)
            op = op % 100

        if op == 99:
            return True
        elif op == 1:
            self.set_val(self.get_val(arr, pos + 1, parameters[0]) + self.get_val(arr, pos + 2, parameters[1]), arr, pos + 3, parameters[2])
            self.pos = pos + 4
            return False
        elif op == 2:
            self.set_val(self.get_val(arr, pos + 1, parameters[0]) * self.get_val(arr, pos + 2, parameters[1]), arr, pos + 3, parameters[2])
            self.pos = pos + 4
            return False
        elif op == 3:
            if self.first_run:
                self.set_val(self.phase_setting, arr, pos + 1, parameters[0])
                self.first_run = False
                self.pos = pos + 2
                return False
            elif not self.first_run and self.first_producer:
                self.set_val(0, arr, pos + 1, parameters[0])
                self.first_run = False
                self.first_producer = False
                self.pos = pos + 2
                return False
            else:
                with self.consume:
                    while len(self.queue_dict[self.dependency_key]) == 0:
                        self.consume.wait()
                    self.set_val(self.queue_dict[self.dependency_key].popleft(), arr, pos + 1, parameters[0])
                self.pos = pos + 2
                return False
        elif op == 4:
            with self.produce:
                self.queue_dict[self.phase_setting].append(self.get_val(arr, pos + 1, parameters[0]))
                self.produce.notifyAll()
            self.pos = pos + 2
            return False
        elif op == 5:
            if self.get_val(arr, pos + 1, parameters[0]) != 0:
                self.pos = self.get_val(arr, pos + 2, parameters[1])
                return False
            else:
                self.pos = pos + 3
                return False
        elif op == 6:
            if self.get_val(arr, pos + 1, parameters[0]) == 0:
                self.pos = pos + self.get_val(arr, pos + 2, parameters[1])
                return False
            else:
                self.pos = pos + 3
                return False
        elif op == 7:
            if self.get_val(arr, pos + 1, parameters[0]) < self.get_val(arr, pos + 2, parameters[1]):
                self.set_val(1, arr, pos + 3, parameters[2])
            else:
                self.set_val(0, arr, pos + 3, parameters[2])
            self.pos = pos + 4
            return False
        elif op == 8:
            if self.get_val(arr, pos + 1, parameters[0]) == self.get_val(arr, pos + 2, parameters[1]):
                self.set_val(1, arr, pos + 3, parameters[2])
            else:
                self.set_val(0, arr, pos + 3, parameters[2])
            self.pos = pos + 4
            return False
        elif op == 9:
            self.relative_base = self.relative_base + self.get_val(arr, pos + 1, parameters[0])
            self.pos = pos + 2
            return False
        else:
            print("Uknown op code " + str(op) + "at position " + str(pos))
            return False
