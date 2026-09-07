import numpy as np
import cv2
import time

WIDTH = 120
HEIGHT = 80

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
        "color" : [0, 255, 0]
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
        [0, 1, 3],
        [1, 2, 3],
        [0, 1, 4],
        [1, 4, 5],
        [1, 2, 5],
        [2, 5, 6],
        [2, 3, 6],
        [3, 6, 7],
        [0, 3, 7],
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
    # AB = B - A
    # AP = P - A
    # return (AB[0] * AP[1]) - (AB[1] * AP[0])
    return ((B[0] - A[0]) * (P[1] - A[1])) - ((B[1] - A[1]) * (P[0] - A[0]))


def rander(image, triangle, f, depth_map):
    color = triangle["color"]

    pt1 = mapping(triangle["pos"][0], f)
    pt2 = mapping(triangle["pos"][1], f)
    pt3 = mapping(triangle["pos"][2], f)

    A = pt1["pos"].astype(int)
    B = pt2["pos"].astype(int)
    C = pt3["pos"].astype(int)

    # BA = pt1["pos"] - pt2["pos"]
    # CB = pt2["pos"] - pt3["pos"]
    # AC = pt3["pos"] - pt1["pos"]

    MaxX = min(max(A[0], B[0], C[0]), WIDTH)
    MinX = max(min(A[0], B[0], C[0]), 0)
    MaxY = min(max(A[1], B[1], C[1]), HEIGHT)
    MinY = max(min(A[1], B[1], C[1]), 0)
    
    
    
    # print(MaxX, MaxY)

    for i in range(MinX, MaxX):
        for j in range(MinY, MaxY):
            w1 = cross(A, B, [i, j])
            w2 = cross(B, C, [i, j])
            w3 = cross(C, A, [i, j])
            if (w1 >= 0 and w2 >= 0 and w3 >= 0) or (w1 <= 0 and w2 <= 0 and w3 <= 0):
                temp = w1 + w2 + w3
                w1 = w1 / temp
                w2 = w2 / temp
                w3 = w3 / temp
                depth = w1 * pt1["depth"] + w2 * pt2["depth"] + w3 * pt3["depth"]
                
                if(depth_map[j][i] > depth):
                    
                    image[j, i] = (color)
                    depth_map[j][i] = depth
                
            


    

    # cv2.line(image, A, B, (0, 255, 0), 1)
    # cv2.line(image, A, C, (0, 255, 0), 1)
    # cv2.line(image, B, C, (0, 255, 0), 1)

    # cv2.circle(image, A, 5, (255, 255, 255), -1)
    # cv2.circle(image, B, 5, (255, 255, 255), -1)
    # cv2.circle(image, C, 5, (255, 255, 255), -1)


def main():

    camera = {
        "pos" : np.array([0, 0, -100]),
        "rotation" : np.array([0.0, 0.0, 0.0]),
        "f" : 60 #320
    }
    while(True):
        start_time = time.time()

        pointsTriangle = []
        depth_map = np.full((HEIGHT, WIDTH), np.inf)
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
            # points.append(temp_points)


        # 渲染
        for triangle in pointsTriangle:
            rander(image, triangle, camera["f"], depth_map)


        display_image = cv2.resize(
            image,
            (120 * 5, 80 * 5),
            interpolation=cv2.INTER_NEAREST
        )
                
        cv2.imshow("3D Renderer", display_image)

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
        FPS = 1 / max(end_time - start_time, 0.000001)
        print("FPS", FPS)

        


if __name__ == "__main__":
    main()