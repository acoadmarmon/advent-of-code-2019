from collections import deque

def init_intcode_run(arr, pos, phase_setting, dependency, queue, first_run, first_producer, consume, produce):
    return IntcodeProgram(arr, pos, phase_setting, dependency, queue, first_run, first_producer, consume, produce)

class IntcodeProgram:
    def __init__(self, arr, pos, phase_setting, dependency, queue, first_run, first_producer, consume, produce):
        self.phase_setting = phase_setting
        self.first_producer = first_producer
        self.first_run = first_run
        self.dependency= dependency
        self.consume = consume
        self.produce = produce
        self.queue = queue
        self.intcode_parser(arr, pos)

    def get_val(self, arr, position, parameter=0):
        if parameter:
            return arr[position]
        else:
            return arr[arr[position]]

    def intcode_parser(self, arr, pos):
        op = arr[pos]
        parameters = (0, 0, 0)
        if op > 99:
            parameters = ((op // 100) % 10, (op // 1000) % 10, (op // 10000) % 10)
            op = op % 100

        if op == 99:
            return True
        elif op == 1:
            arr[arr[pos + 3]] = self.get_val(arr, pos + 1, parameters[0]) + self.get_val(arr, pos + 2, parameters[1])
            return self.intcode_parser(arr, pos + 4)
        elif op == 2:
            arr[arr[pos + 3]] = self.get_val(arr, pos + 1, parameters[0]) * self.get_val(arr, pos + 2, parameters[1])
            return self.intcode_parser(arr, pos + 4)
        elif op == 3:
            if self.first_run:
                arr[arr[pos + 1]] = self.phase_setting
                self.first_run = False
                return self.intcode_parser(arr, pos + 2)
            elif not self.first_run and self.first_producer:
                arr[arr[pos + 1]] = 0
                self.first_run = False
                self.first_producer = False
                return self.intcode_parser(arr, pos + 2)
            else:
                with self.consume:
                    while len(self.queue[self.dependency]) == 0:
                        self.consume.wait()
                    arr[arr[pos + 1]] = self.queue[self.dependency].popleft()
                return self.intcode_parser(arr, pos + 2)
        elif op == 4:
            with self.produce:
                self.queue[self.phase_setting].append(self.get_val(arr, pos + 1, parameters[0]))
                self.produce.notifyAll()
            return self.intcode_parser(arr, pos + 2)
        elif op == 5:
            if self.get_val(arr, pos + 1, parameters[0]) != 0:
                return self.intcode_parser(arr, self.get_val(arr, pos + 2, parameters[1]))
            else:
                return self.intcode_parser(arr, pos + 3)
        elif op == 6:
            if self.get_val(arr, pos + 1, parameters[0]) == 0:
                return self.intcode_parser(arr, self.get_val(arr, pos + 2, parameters[1]))
            else:
                return self.intcode_parser(arr, pos + 3)
        elif op == 7:
            if self.get_val(arr, pos + 1, parameters[0]) < self.get_val(arr, pos + 2, parameters[1]):
                arr[arr[pos + 3]] = 1
            else:
                arr[arr[pos + 3]] = 0
            return self.intcode_parser(arr, pos + 4)
        elif op == 8:
            if self.get_val(arr, pos + 1, parameters[0]) == self.get_val(arr, pos + 2, parameters[1]):
                arr[arr[pos + 3]] = 1
            else:
                arr[arr[pos + 3]] = 0
            return self.intcode_parser(arr, pos + 4)
        else:
            print("Uknown op code " + str(op) + "at position " + str(pos))
            return False
