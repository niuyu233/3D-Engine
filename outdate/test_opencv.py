import numpy as np
import cv2
import time

# WIDTH = int(640 / 4)
# HEIGHT = int(480 / 4)
WIDTH = 640
HEIGHT = 480

map = [
    {
        "type" : "cube",
        "pos" : np.array([0, 0, 0]),
        "size" : np.array([50, 30, 20]),
        "rotation" : np.array([0, 0, 0]),
        "color" : [255, 0, 0]
    },
    {
        "type" : "cube",
        "pos" : np.array([100, 0, 0]),
        "size" : np.array([50, 30, 20]),
        "rotation" : np.array([0, 0, 0]),
        "color" : [0, 0, 255]
    }
]

modelPoints = {
    "cube" : np.array([
                [0, 0, 0],#    /7--/6
                [1, 0, 0],#  4/--5/ |
                [1, 0, 1],#  |  3| /2
                [0, 0, 1],#  0---1/
                [0, 1, 0],
                [1, 1, 0],
                [1, 1, 1],
                [0, 1, 1]
    ])
}

triangle = {
    "cube" : np.array([
        [0, 3, 1],
        [3, 2, 1],
        [0, 1, 4],
        [1, 5, 4],
        [1, 2, 5],
        [2, 6, 5],
        [2, 3, 6],
        [3, 7, 6],
        [3, 0, 7],
        [0, 4, 7],
        [4, 5, 6],
        [4, 6, 7],
    ])
}


# 世界坐标-摄像头坐标
def camera_convert(point, camera):
    point -= camera["pos"]

    theta = camera["rotation"][0]
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta),  np.cos(theta)]
    ])
    point = Rx @ point

    theta = camera["rotation"][1]
    Ry = np.array([
        [ np.cos(theta), 0, np.sin(theta)],
        [0,              1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    point = Ry @ point

    theta = camera["rotation"][2]
    Rz = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0,              0,             1]
    ])
    point = Rz @ point

    return point

# 拆分三角形(摄像头坐标)
def divide(pointsTriangle, type, points, color):
    for i in triangle[type]:
        # pointsTriangle.append([points[i[0]], points[i[1]], points[i[2]]])
        if points[i[0]][2] > 0 and points[i[1]][2] > 0 and points[i[2]][2] > 0:
            temp = {
                "pos" : [points[i[0]], points[i[1]], points[i[2]]],
                "color" : color
            }
            pointsTriangle.append(temp)

# 投影到屏幕上
def mapping(point, f):
    # if point[2] == 0:
    #     point[2] = 0.0001
    u = f * point[0] / point[2] + WIDTH / 2
    v = f * point[1] / point[2] + HEIGHT / 2
    z = point[2]
    pt = {
        "pos" : np.array([u, v]),
        "depth" : z
    }
    return pt

def cross(A, B, P):
    return ((B[0] - A[0]) * (P[1] - A[1])) - ((B[1] - A[1]) * (P[0] - A[0]))


def Back_Face_Culling(randerTriangle, pointsTriangle):
    for Triangle in pointsTriangle:
        A = Triangle["pos"][0]
        B = Triangle["pos"][1]
        C = Triangle["pos"][2]

        N = np.cross(B - A, C - A)
        if np.dot(N, -A) < 0:
            randerTriangle.append(Triangle)





def rander(image, triangle, f, depth_map):
    color = triangle["color"]

    pt1 = mapping(triangle["pos"][0], f)
    pt2 = mapping(triangle["pos"][1], f)
    pt3 = mapping(triangle["pos"][2], f)

    A = pt1["pos"].astype(int)
    B = pt2["pos"].astype(int)
    C = pt3["pos"].astype(int)


    # 矩形范围
    MaxX = min(max(A[0], B[0], C[0]), WIDTH)
    MinX = max(min(A[0], B[0], C[0]), 0)
    MaxY = min(max(A[1], B[1], C[1]), HEIGHT)
    MinY = max(min(A[1], B[1], C[1]), 0)

    area = cross(A, B, C)
    if(area == 0):
        return

    xs = np.arange(MinX, MaxX)
    xs_A0 = (xs - A[0])
    xs_B0 = (xs - B[0])
    xs_C0 = (xs - C[0])

    ys = np.arange(MinY, MaxY)
    ys_A1 = (ys - A[1])
    ys_B1 = (ys - B[1])
    ys_C1 = (ys - C[1])

    # X, Y = np.meshgrid(xs, ys)

    # 计算三个edge function
    w1 = ((B[0] - A[0]) * ys_A1[:, None] - (B[1] - A[1]) * xs_A0[None,:])
    w2 = ((C[0] - B[0]) * ys_B1[:, None] - (C[1] - B[1]) * xs_B0[None,:])
    w3 = ((A[0] - C[0]) * ys_C1[:, None] - (A[1] - C[1]) * xs_C0[None,:])
    # w1 = ((B[0] - A[0]) * (Y - A[1]) - (B[1] - A[1]) * (X - A[0]))
    # w2 = ((C[0] - B[0]) * (Y - B[1]) - (C[1] - B[1]) * (X - B[0]))
    # w3 = ((A[0] - C[0]) * (Y - C[1]) - (A[1] - C[1]) * (X - C[0]))

    if area > 0:
        inside = (w1 >= 0) & (w2 >= 0) & (w3 >= 0)
    else:
        inside = (w1 <= 0) & (w2 <= 0) & (w3 <= 0)
    
    if not np.any(inside):
        return

    # 重心坐标
    alpha = w1 / area
    beta  = w2 / area
    gamma = w3 / area

    # 这个三角形的四边形的深度图
    depth = (alpha * pt1["depth"] + beta * pt2["depth"] + gamma * pt3["depth"])

    depth_part = depth_map[MinY:MaxY, MinX:MaxX]
    mask = inside & (depth < depth_part)
    depth_part[mask] = depth[mask]
    image_part = image[MinY:MaxY, MinX:MaxX]
    image_part[mask] = color

    cv2.line(image, A, B, (0, 255, 0), 1)
    cv2.line(image, A, C, (0, 255, 0), 1)
    cv2.line(image, B, C, (0, 255, 0), 1)

    # cv2.circle(image, A, 5, (255, 255, 255), -1)
    # cv2.circle(image, B, 5, (255, 255, 255), -1)
    # cv2.circle(image, C, 5, (255, 255, 255), -1)


def main():
    FPS = 0
    camera = {
        "pos" : np.array([-11, 12, 9]),
        "rotation" : np.array([ 0.0, -1.5, 0.0]),
        "f" : 320
    }
    while(True):
        start_time = time.time()

        pointsTriangle = []
        randerTriangle = []
        depth_map = np.full((HEIGHT, WIDTH), np.inf, dtype=np.float32)
        image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)


        # 映射
        for model in map:
            type = model["type"]
            color = model["color"]
            temp_points = []
            for i in modelPoints[type]:
                point = model["pos"] + i * model["size"]
                point = camera_convert(point, camera)
                temp_points.append(point)

            divide(pointsTriangle, type, temp_points, color)
        
        Back_Face_Culling(randerTriangle, pointsTriangle)

        time1 = time.time()

        # 渲染
        for triangle in randerTriangle:
            rander(image, triangle, camera["f"], depth_map)

        time2 = time.time()
        
        cv2.putText(
            image,
            str(int(FPS)),          # 要显示的文字
            (0, 12),               # 左下角坐标
            cv2.FONT_HERSHEY_SIMPLEX,# 字体
            0.5,                     # 字体大小
            (255, 255, 0),             # BGR颜色：绿色
            1                       # 线宽
        )
        display_image = cv2.resize(
            image,
            (640, 480),
            interpolation=cv2.INTER_NEAREST
        )
        
        cv2.imshow("3D Renderer", display_image)

        time3 = time.time()

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == ord('w'):
            camera["pos"][2] += 1.0
        elif key == ord('s'):
            camera["pos"][2] -= 1.0
        elif key == ord('a'):
            camera["pos"][0] -= 1.0
        elif key == ord('d'):
            camera["pos"][0] += 1.0
        elif key == ord('q'):
            camera["pos"][1] += 1.0
        elif key == ord('e'):
            camera["pos"][1] -= 1.0
        elif key == ord('1'):
            camera["rotation"][1] += 0.05
        elif key == ord('3'):
            camera["rotation"][1] -= 0.05
        elif key == ord('5'):
            camera["rotation"][0] -= 0.05
        elif key == ord('2'):
            camera["rotation"][0] += 0.05

        end_time = time.time()

        total_time = (end_time - start_time)
        if(total_time > 0):
            print("part1:\t", (time1 - start_time) / total_time)
            print("rander:\t", (time2 - time1) / total_time)
            print("cv:\t", (time3 - time2) / total_time)
            print("key:\t", (end_time - time3) / total_time)
            FPS = 1 / total_time
            print("fps:", FPS)
        
        # print("pos:", camera["pos"])
        # print("rotation:", camera["rotation"])

        


if __name__ == "__main__":
    main()