import numpy as np
import cv2
import time
import pygame

# WIDTH = int(640 / 4)
# HEIGHT = int(480 / 4)
WIDTH = 640
HEIGHT = 480

map = [
    {
        "type" : "cube",
        "pos" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [255, 0, 0]
    },
    {
        "type" : "cube",
        "pos" : np.array([100.0, 0.0, 0.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [0, 0, 255]
    },
    {
        "type" : "cube",
        "pos" : np.array([200.0, 0.0, 0.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [0, 255, 0]
    },
    {
        "type" : "cube",
        "pos" : np.array([0.0, 0.0, 40.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [0, 255, 255]
    },
    {
        "type" : "cube",
        "pos" : np.array([0.0, 0.0, 80.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [255, 0, 255]
    },
    {
        "type" : "cube",
        "pos" : np.array([0.0, 0.0, 120.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [255, 255, 0]
    },
    {
        "type" : "cube",
        "pos" : np.array([0.0, 60.0, 0.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [0, 128, 128]
    },
    {
        "type" : "cube",
        "pos" : np.array([0.0, 120.0, 0.0], dtype=np.float32),
        "size" : np.array([50, 30, 20], dtype=np.float32),
        "rotation" : np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "color" : [128, 0, 128]
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


pygame.init()

def get_rotation_matrix(rotation):
    theta_x, theta_y, theta_z = rotation

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(theta_x), -np.sin(theta_x)],
        [0, np.sin(theta_x),  np.cos(theta_x)]
    ])

    Ry = np.array([
        [ np.cos(theta_y), 0, np.sin(theta_y)],
        [0, 1, 0],
        [-np.sin(theta_y), 0, np.cos(theta_y)]
    ])

    Rz = np.array([
        [np.cos(theta_z), -np.sin(theta_z), 0],
        [np.sin(theta_z),  np.cos(theta_z), 0],
        [0, 0, 1]
    ])

    return Rz, Ry, Rx

# 世界坐标-摄像头坐标
def camera_convert(point, camera, R):
    point -= camera["pos"]
    point = R @ point

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

# 剔除背面三角形
def Back_Face_Culling(randerTriangle, pointsTriangle):
    for Triangle in pointsTriangle:
        A = Triangle["pos"][0]
        B = Triangle["pos"][1]
        C = Triangle["pos"][2]

        N = np.cross(B - A, C - A)
        if np.dot(N, -A) < 0:
            randerTriangle.append(Triangle)

# 映射
def map_to_camera(pointsTriangle, map, camera, R):

    for model in map:
        type = model["type"]
        color = model["color"]
        temp_points = []
        for i in modelPoints[type]:
            point = model["pos"] + i * model["size"]
            point = camera_convert(point, camera, R)
            temp_points.append(point)
        divide(pointsTriangle, type, temp_points, color)

def update_camera(camera, keys, RzT, RyT, RxT, dx, dy, FPS):
    
    forward = np.array([0, 0, 1])
    right = np.array([1, 0, 0])
    up = np.array([0, 1, 0])
    forward = RyT @ RxT @ RzT @ forward
    right = RyT @ RxT @ RzT @ right
    up = RyT @ RxT @ RzT @ up

    speed = 1.0 / (FPS / 60.0)
    if keys[pygame.K_w]:
        camera["pos"] += forward * speed
    if keys[pygame.K_s]:
        camera["pos"] -= forward * speed
    if keys[pygame.K_a]:
        camera["pos"] -= right * speed
    if keys[pygame.K_d]:
        camera["pos"] += right * speed
    if keys[pygame.K_q]:
        camera["pos"] += up * speed
    if keys[pygame.K_e]:
        camera["pos"] -= up * speed

    camera["rotation"][1] -= dx * 0.005
    camera["rotation"][0] += dy * 0.005

    # if keys[pygame.K_u]:
    #     camera["rotation"][2] += 0.05 * speed
    # if keys[pygame.K_j]:
    #     camera["rotation"][2] -= 0.05 * speed

def rander(image, triangle, f, depth_map):
    color = triangle["color"]

    pt1 = mapping(triangle["pos"][0], f)
    pt2 = mapping(triangle["pos"][1], f)
    pt3 = mapping(triangle["pos"][2], f)

    A = pt1["pos"].astype(np.int32)
    B = pt2["pos"].astype(np.int32)
    C = pt3["pos"].astype(np.int32)


    # 矩形范围
    MaxX = min(max(A[0], B[0], C[0]), WIDTH)
    MinX = max(min(A[0], B[0], C[0]), 0)
    MaxY = min(max(A[1], B[1], C[1]), HEIGHT)
    MinY = max(min(A[1], B[1], C[1]), 0)

    area = cross(A, B, C)
    if(area == 0):
        return

    xs = np.arange(MinX, MaxX, dtype=np.int32)
    xs_A0 = (xs - A[0])
    xs_B0 = (xs - B[0])
    xs_C0 = (xs - C[0])

    ys = np.arange(MinY, MaxY, dtype=np.int32)
    ys_A1 = (ys - A[1])
    ys_B1 = (ys - B[1])
    ys_C1 = (ys - C[1])

    # X, Y = np.meshgrid(xs, ys)

    # 计算三个edge function
    w1 = ((B[0] - A[0]) * ys_A1[None,:] - (B[1] - A[1]) * xs_A0[:, None])
    w2 = ((C[0] - B[0]) * ys_B1[None,:] - (C[1] - B[1]) * xs_B0[:, None])
    w3 = ((A[0] - C[0]) * ys_C1[None,:] - (A[1] - C[1]) * xs_C0[:, None])
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

    depth_part = depth_map[MinX:MaxX, MinY:MaxY]
    mask = inside & (depth < depth_part)
    depth_part[mask] = depth[mask]
    image_part = image[MinX:MaxX, MinY:MaxY]
    image_part[mask] = color

    # cv2.line(image, A, B, (0, 255, 0), 1)
    # cv2.line(image, A, C, (0, 255, 0), 1)
    # cv2.line(image, B, C, (0, 255, 0), 1)

    # cv2.circle(image, A, 5, (255, 255, 255), -1)
    # cv2.circle(image, B, 5, (255, 255, 255), -1)
    # cv2.circle(image, C, 5, (255, 255, 255), -1)


def main():
    FPS = 60
    camera = {
        "pos" : np.array([-11, 12, 9], dtype=np.float32),
        "rotation" : np.array([ 0.0, -1.5, 0.0], dtype=np.float32),
        "f" : 320
    }

    

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Renderer")

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    running = True
    while running:
        start_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pointsTriangle = []
        randerTriangle = []
        depth_map = np.full((WIDTH, HEIGHT), np.inf, dtype=np.float32)
        image = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)

        Rz, Ry, Rx = get_rotation_matrix(camera["rotation"])
        keys = pygame.key.get_pressed()
        dx, dy = pygame.mouse.get_rel()
        update_camera(camera, keys, Rz.T, Ry.T, Rx.T, dx, dy, FPS)
        
        map_to_camera(pointsTriangle, map, camera, (Rz @ Rx @ Ry))
        Back_Face_Culling(randerTriangle, pointsTriangle)

        time1 = time.time()

        # 渲染
        for triangle in randerTriangle:
            rander(image, triangle, camera["f"], depth_map)

        time2 = time.time()
        

        surface = pygame.surfarray.make_surface(
            np.transpose(
                image,
                (0,1,2)
            )
        )
        screen.blit(surface, (0,0))
        pygame.display.flip()



        end_time = time.time()

        total_time = max((end_time - start_time), 1e-6)
        
        FPS = 1 / total_time
        #     print("part1:\t", (time1 - start_time) / total_time)
        #     print("rander:\t", (time2 - time1) / total_time)
        #     print("key:\t", (end_time - time3) / total_time)
        #     
        #     print("fps:", FPS)
        
        # print("pos:", camera["pos"])
        # print("rotation:", camera["rotation"])

        


if __name__ == "__main__":
    main()