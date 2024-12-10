from queue import PriorityQueue


class AStar:
    def __init__(self, grid):
        self.grid = grid

    def heuristic(self, a, b):
        """ Функция эвристики Манхэттенского расстояния """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def search(self, start, goal):
        """ Поиск пути от start до end """
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            _, current = frontier.get()

            if current == goal:
                return self.reconstruct_path(came_from, start, goal)

            for next in self.grid.neighbors(current):
                # Определяем, является ли ход диагональным (если обе координаты изменились)
                step_cost = 1.41 if next[0] != current[0] and next[1] != current[1] else 1
                new_cost = cost_so_far[current] + step_cost

                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current

        return None  # Если путь не найден

    def reconstruct_path(self, came_from, start, goal):
        """ Восстановление пути от end до start """
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
