class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.obstacles = set()

    def add_obstacle(self, position):
        """Добавление препятствия на сетку"""
        x, y = position
        self.grid[x][y] = 1  # Помечаем клетку как препятствие (1)
        self.obstacles.add(position)

    def is_obstacle(self, position):
        """Проверка, является ли клетка препятствием"""
        return position in self.obstacles

    def is_within_bounds(self, position):
        """Проверяет, находится ли позиция в пределах сетки """
        x, y = position
        return 0 <= x < self.rows and 0 <= y < self.cols

    def is_walkable(self, position):
        """Проверка, можно ли пройти через клетку (не препятствие и в пределах карты)"""
        return self.is_within_bounds(position) and not self.is_obstacle(position)

    def neighbors(self, position):
        """Возвращает соседние клетки (в пределах карты и проходимые)"""
        x, y = position
        candidates = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        # Возвращаем только клетки, которые в пределах карты и не являются препятствиями
        return [pos for pos in candidates if self.is_walkable(pos)]
