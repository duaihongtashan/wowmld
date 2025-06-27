import cv2
import numpy as np
import heapq
from PIL import Image,ImageDraw


class Node:
    """
    表示A*算法中的节点。
    每个节点包含从起点到当前节点的实际代价（g值）、启发式代价（h值）以及总代价（f值）。
    此外，还包含指向父节点的引用和当前节点的位置。
    """
    def __init__(self, parent=None, position=None):
        """
        初始化节点。

        :param parent: 父节点，表示如何到达当前节点的上一个节点。在路径重构时用到。默认为None。
        :param position: 节点的位置，通常是一个(x, y)坐标。默认为None。
        :param g: 从起点到当前节点的实际代价。在节点创建时默认为0，后续根据路径长度更新。
        :param h: 从当前节点到终点的启发式代价。在节点创建时默认为0，后续根据启发式函数计算。
        :param f: 总代价，等于g值加h值。在节点创建时默认为0，后续根据g和h的值计算。
        """
        self.parent = parent  # 父节点，用于路径回溯
        self.position = position  # 节点的位置坐标
        self.g = 0  # 从起点到当前节点的代价
        self.h = 0  # 从当前节点到终点的启发式代价
        self.f = 0  # 总代价，f = g + h

    def __lt__(self, other):
        """
        定义节点之间的比较操作，用于优先队列。
        如果当前节点的f值小于另一个节点的f值，则当前节点较小。
        如果两个节点的f值相等，则比较h值，h值较小的节点较小。

        :param other: 要比较的另一个节点。
        :return: 如果当前节点小于另一个节点，则返回True；否则返回False。
        """
        # 当前节点的f值小于另一个节点的f值，或者f值相等但h值较小
        return self.f < other.f or (self.f == other.f and self.h < other.h)

class AStar:

    def __init__(self, grid, start, end):
        """
        初始化路径查找器。

        :param grid: 游戏网格，通常是一个二维列表或数组，表示可通行和不可通行的区域。
        :param start: 起点的坐标，通常是一个元组(x, y)。
        :param end: 终点的坐标，通常是一个元组(x, y)。
        :param open_list: 开放列表，用于存储待评估的节点，实现为优先队列。
        :param closed_list: 关闭列表，用于存储已评估的节点，实现为集合以避免重复处理。
        :param heuristic: 启发式函数，用于计算启发式代价h。默认为曼哈顿距离。
        """
        self.grid = grid  # 游戏网格
        self.start = Node(position=start)  # 起点节点
        self.end = Node(position=end)  # 终点节点
        self.open_list = []  # 开放列表，初始化为空列表，后续将作为优先队列使用
        self.closed_list = set()  # 关闭列表，初始化为空集合
        self.heuristic = self.manhattan_distance  # 启发式函数，默认为曼哈顿距离
        self.init_heuristic()  # 初始化启发式代价和总代价，并将起点加入开放列表

        # 使用heapq.heapify将开放列表转换为优先队列
        heapq.heapify(self.open_list)

    def init_heuristic(self):
        """
        初始化启发式代价和总代价，并将起点加入开放列表。
        """
        # 计算起点到终点的启发式代价h
        self.start.h = self.heuristic(self.start.position, self.end.position)
        # 计算起点的总代价f（g初始化为0，因为起点没有前驱节点）
        self.start.f = self.start.g + self.start.h
        # 将起点加入开放列表（优先队列），以便后续处理
        heapq.heappush(self.open_list, self.start)  # 注意：这里实际上是不必要的，因为已经在__init__中heapify了，但显式push可以保持代码清晰

        # 注意：heapq.heappush在这里实际上是多余的，因为我们在__init__中已经使用heapq.heapify将self.open_list转换为了一个有效的堆。
        # 如果你在init_heuristic之前或之后向self.open_list添加元素，它们会自动按照堆的性质排列。
        # 因此，这里的heapq.heappush可以移除，除非你在init_heuristic之后又手动修改了self.open_list的内容（例如，添加了除start之外的其他节点）。


    def manhattan_distance(self, a, b):
        """
        计算两点之间的曼哈顿距离。

        :param a: 第一个点的坐标，形式为(x, y)。
        :param b: 第二个点的坐标，形式为(x, y)。
        :return: 两点之间的曼哈顿距离。
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def euclidean_distance(self, a, b):
        """
        计算两点之间的欧几里得距离。

        :param a: 第一个点的坐标，形式为(x, y)。
        :param b: 第二个点的坐标，形式为(x, y)。
        :return: 两点之间的欧几里得距离。
        """
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def get_neighbors(self, node):
        """
        获取给定节点的所有相邻节点。

        :param node: 当前节点，其position属性表示节点的坐标。
        :return: 当前节点的所有相邻节点的列表。相邻节点是指上下左右四个方向的节点。
        """
        neighbors = []  # 用于存储相邻节点的列表

        # 遍历四个方向：上、下、左、右
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            # 计算新位置
            node_position = (node.position[0] + new_position[0], node.position[1] + new_position[1])
            # 检查新位置是否在网格范围内且是可通行的（假设网格中0表示可通行，其他值表示不可通行）
            # 提取节点位置的x和y坐标
            y, x = node_position

            # 验证x和y坐标是否在网格的有效范围内
            is_within_bounds = 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0])

            # 检查指定位置的网格是否为可通行（假设0表示可通行）
            is_walkable = self.grid[y][x] == 0

            # 最终判断该节点位置是否有效且可通行
            if is_within_bounds and is_walkable:

                # 创建一个新节点，并将其添加到相邻节点列表中
                neighbor = Node(parent=node, position=node_position)
                # 设置新节点的g值为当前节点的g值加1（假设移动代价为1）
                neighbor.g = node.g + 1
                # 使用启发式函数计算新节点的h值
                neighbor.h = self.heuristic(neighbor.position, self.end.position)
                # 计算新节点的f值
                neighbor.f = neighbor.g + neighbor.h
                neighbors.append(neighbor)
        return neighbors

    def reconstruct_path(self, node):
        """
        从给定节点回溯重建路径。

        :param node: 目标节点，通常是终点节点或路径上的某个节点。
        :return: 从起点到目标节点的路径，形式为节点坐标的列表。
        """
        path = []  # 用于存储路径的列表
        # 从目标节点开始，回溯到起点节点
        while node is not None:
            path.append(node.position)  # 将当前节点坐标添加到路径列表中
            node = node.parent  # 移动到父节点
        # 由于路径是从目标节点回溯到起点节点的，所以需要反转列表以得到正确的顺序
        return path[::-1]

    # 注意：Node类应该已经定义，并且具有position和parent属性。此外，heuristic属性或方法应该能够根据当前情况选择合适的启发式函数（如曼哈顿距离或欧几里得距离）。

    def search(self):
        """
        使用A*算法搜索从起点到终点的最短路径。

        :return: 从起点到终点的最短路径，形式为节点坐标的列表。如果找不到路径，则返回None。
        """
        # 当开放列表（open_list）不为空时，继续搜索
        while self.open_list:
            # 从开放列表中弹出具有最低f值的节点（优先队列的堆顶元素）
            current_node = heapq.heappop(self.open_list)
            # 将当前节点的位置添加到关闭列表（closed_list）中，表示已经访问过
            self.closed_list.add(current_node.position)

            # 如果当前节点的位置是终点位置，则通过回溯重建路径并返回
            if current_node.position == self.end.position:
                return self.reconstruct_path(current_node)

            # 获取当前节点的所有相邻节点
            for neighbor in self.get_neighbors(current_node):
                # 如果相邻节点的位置已经在关闭列表中，则跳过该节点
                if neighbor.position in self.closed_list:
                    continue

                # 检查开放列表中是否已经有具有相同位置和更低g值的节点
                # 如果有，则跳过当前相邻节点，因为A*算法保证不会通过更差的路径到达同一节点
                if any(open_node.position == neighbor.position and open_node.g <= neighbor.g for open_node in
                       self.open_list):
                    continue

                # 将相邻节点添加到开放列表中，以便后续处理
                heapq.heappush(self.open_list, neighbor)

        # 如果开放列表为空且没有找到终点，则返回None表示没有路径
        return None

    # 注意：
    # 1. self.open_list 应该是一个优先队列（通常使用heapq模块实现），其中存储了待处理的节点。
    # 2. self.closed_list 应该是一个集合，用于存储已经访问过的节点位置，以避免重复访问。
    # 3. self.end 是终点节点，其position属性表示终点的坐标。
    # 4. self.get_neighbors 方法应该返回给定节点的所有相邻节点。
    # 5. self.reconstruct_path 方法应该根据节点的parent属性回溯重建路径。
    # 6. Node类应该已经定义，并且具有position, parent, g, h, 和 f属性。


def image_to_grid(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # 获取图像的宽度和高度
    height, width, _ = image.shape

    # 创建网格
    grid = []

    for y in range(height):
        row = []
        for x in range(width):
            pixel = image[y, x]
            # 判断像素值，如果是黑色则不可通行，其他颜色则可通行
            # if np.array_equal(pixel, [0, 0, 0]):  # 黑色
            #     row.append(1)  # 不可通行
            # else:  # 白色或其他颜色
            #     row.append(0)  # 可通行
            if np.all(pixel < [15, 15, 15]):  # 判断像素是否接近黑色
                row.append(1)  # 不可通行
            else:
                row.append(0)  # 可通行


        grid.append(row)

    # # 显示网格（这里简单地将网格保存为图像，也可以选择其他方式显示）
    # # 注意：这种方法只是将网格数据转换为图像，用于可视化，不是真正的网格显示
    # grid_image = np.array(grid, dtype=np.uint8) * 255  # 将0变为黑色，1变为白色（反转颜色）
    # grid_image = cv2.resize(grid_image, (width, height), interpolation=cv2.INTER_NEAREST)
    # grid_image = cv2.cvtColor(grid_image, cv2.COLOR_GRAY2BGR)  # 转换为彩色图像（白色背景）
    # cv2.imshow('Grid Image', grid_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 返回网格和起终点位置（这里假设起终点位置不变）
    return grid

# 封装后的A*寻路函数
def a_star_search_from_image(image_path,start, end):
    # 读取地图并转换为网格
    grid = image_to_grid(image_path)
    astar = AStar(grid, start, end)
    path = astar.search()

    # if path is not None:
    #     image = Image.open(image_path)  # 打开图像
    #     # 创建一个绘图对象
    #     draw = ImageDraw.Draw(image)
    #     # 绘制路径（使用红色线条）
    #     converted_path = [(y_x[1], y_x[0]) for y_x in path]
    #     draw.line(converted_path, fill='red', width=5)
    #
    #     # 显示图像
    #     image.show()

    return path


# # Example usage:
# if __name__ == "__main__":
#
#     image_path = "../map/black_map.bmp"  # 设置你的地图图像路径
#
#     path = a_star_search_from_image(image_path,(180,192),(239,231))
#     print("寻路路径:", path)
#
#
#     image = Image.open(image_path)  # 打开图像
#     # 创建一个绘图对象
#     draw = ImageDraw.Draw(image)
#     # 绘制路径（使用红色线条）
#     converted_path = [(y_x[1], y_x[0]) for y_x in path]
#     draw.line(converted_path, fill='red', width=5)
#
#     # 显示图像
#     image.show()

