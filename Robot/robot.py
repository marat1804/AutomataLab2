look = {
    '0': 'right',
    '1': 'down',
    '2': 'left',
    '3': 'up'
}

cells = {
    ' ': 'EMPTY',
    'e': 'EXIT',
    'w': 'WALL'
}


class Cell:
    def __init__(self, type, x,y):
        self.type = type

    def __repr__(self):
        return f'{self.type}'


class Robot:
    def __init__(self, x, y, turn, map):
        self.x = x
        self.y = y
        self.turn = turn
        self.map = map

    def __repr__(self):
        return f'''\n x = {self.x}\n y = {self.y}\n turn: {look[str(self.turn)]}'''

    def show(self):
        for row in self.map:
            for cell in row:
                print(cell.type, end=' ')
            print()

    def wall(self):
        count = 1
        if self.turn == 0:
            while self.map[self.y][self.x+count].type == 'EMPTY':
                count += 1
        elif self.turn == 1:
            while self.map[self.y+count][self.x].type == 'EMPTY':
                count += 1
        elif self.turn == 2:
            while self.map[self.y][self.x-count].type == 'EMPTY':
                count += 1
        elif self.turn == 3:
            while self.map[self.y-count][self.x].type == 'EMPTY':
                count += 1
        return count - 1

    def exit(self):
        count = 1
        flag = False
        if self.turn == 0:
            while self.map[self.y][self.x + count].type == 'EMPTY':
                count += 1
            if self.map[self.y][self.x+count].type == 'EXIT':
                flag = True
        elif self.turn == 1:
            while self.map[self.y + count][self.x].type == 'EMPTY':
                count += 1
            if self.map[self.y + count][self.x].type == 'EXIT':
                flag = True
        elif self.turn == 2:
            while self.map[self.y][self.x - count].type == 'EMPTY':
                count += 1
            if self.map[self.y][self.x - count].type == 'EXIT':
                flag = True
        elif self.turn == 3:
            while self.map[self.y - count][self.x].type == 'EMPTY':
                count += 1
            if self.map[self.y - count][self.x].type == 'EXIT':
                flag = True
        return flag

    def right(self):
        self.turn = (self.turn+1) % 4

    def left(self):
        self.turn = (self.turn-1) % 4

    def move(self, count):
        distance = self.wall
        if count > distance:
            return False
        if self.turn == 1:
            if self.turn == 0:
                self.x += count
            elif self.turn == 1:
                self.y += count
            elif self.turn == 2:
                self.x -= count
            elif self.turn == 3:
                self.y -= count
            return True


if __name__ == '__main__':
    r = Robot(0, 0, 3, [])
    r.left()