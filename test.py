import numpy as np
import cv2

WIDTH = 640
HEIGHT = 480

map = [
    {
        "type" : "cube",
        "position" : np.array([0, 0, 0]),
        "size" : np.array([50, 30, 20]),
        "rotation" : np.array([0, 0, 0])
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
# line = [
#     [0, 1],
#     [1, 2],
#     [2, 3],
#     [3, 0], # 1
#     [4, 5],
#     [5, 6],
#     [6, 7],
#     [7, 4], # 2
#     [0, 4],
#     [1, 5],
#     [2, 6],
#     [3, 7]
# ]
triangle = {
    "cube" : np.array([
        [0, 1, 2],
        [0, 2, 3],
        [0, 1, 4],
        [1, 4, 5],
        [1, 2, 5],
        [2, 5, 6],
        [2, 3, 6],
        [3, 6, 7],
        [0, 3, 4],
        [3, 4, 7],
        [4, 5, 6],
        [4, 6, 7],
    ])
}


# 世界坐标-摄像头坐标
def camera_convert(point, camera):
    point -= camera["position"]

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

# 拆分三角形
def divide(pointsTriangle, type, points):
    for i in triangle[type]:
        if points[i[0]][2] > 0 and points[i[1]][2] > 0 and points[i[2]][2] > 0:
            pointsTriangle.append([points[i[0]], points[i[1]], points[i[2]]])

# 投影到屏幕上
def mapping(point, f):
    u = f * point[0] / point[2] + WIDTH / 2
    v = f * point[1] / point[2] + HEIGHT / 2
    z = point[2]
    pt = {
        "position" : [int(u), int(v)],
        "depth" : z
    }
    return pt


def main():

    camera = {
        "position" : np.array([0, 0, -100]),
        "rotation" : np.array([0.0, 0.0, 0.0]),
        "f" : 320
    }
    while(True):
        pointsTriangle = []

        image = np.zeros((480, 640, 3), dtype=np.uint8)


        # 映射
        for model in map:
            type = model["type"]
            temp_points = []
            for i in modelPoints[type]:
                point = model["position"] + i * model["size"]
                point = camera_convert(point, camera)
                temp_points.append(point)

            divide(pointsTriangle, type, temp_points)
            # points.append(temp_points)


        # 渲染
        for trangle in pointsTriangle:
            pt1 = mapping(trangle[0], camera["f"])
            pt2 = mapping(trangle[1], camera["f"])
            pt3 = mapping(trangle[2], camera["f"])



            cv2.line(image, pt1["position"], pt2["position"], (255, 0, 0), 2)
            cv2.line(image, pt1["position"], pt3["position"], (255, 0, 0), 2)
            cv2.line(image, pt2["position"], pt3["position"], (255, 0, 0), 2)

            cv2.circle(image, pt1["position"], 5, (255, 255, 255), -1)
            cv2.circle(image, pt2["position"], 5, (255, 255, 255), -1)
            cv2.circle(image, pt3["position"], 5, (255, 255, 255), -1)




        cv2.imshow("3D Renderer", image)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == ord('w'):
            camera["position"][2] += 1.0
        elif key == ord('s'):
            camera["position"][2] -= 1.0
        elif key == ord('a'):
            camera["position"][0] -= 1.0
        elif key == ord('d'):
            camera["position"][0] += 1.0
        elif key == ord('q'):
            camera["position"][1] += 1.0
        elif key == ord('e'):
            camera["position"][1] -= 1.0
        elif key == ord('1'):
            camera["rotation"][1] += 0.05
        elif key == ord('3'):
            camera["rotation"][1] -= 0.05
        elif key == ord('5'):
            camera["rotation"][0] -= 0.05
        elif key == ord('2'):
            camera["rotation"][0] += 0.05


        


if __name__ == "__main__":
    main()