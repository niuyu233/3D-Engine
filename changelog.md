# 3D-Engine

**v0.3.1	--	2026.9.8**

中文版在后面

**Finished**

- Fixed the bug of covering relationship. The problem is mismatching between barycentric coordinates and their corresponding vertices.
- Use matrix instead of loop in calculating points location.

**完成：**

- 修复遮挡关系的bug，原因在于重心参数w1、w2、w3错位
- 实现矩阵计算生成图形点，取代原本的循环结构



**v0.3	--	2026.9.7**

中文版在后面

**Finished**

- Using pygame to show the window and detecte the key pressing instead of opencv.(FPS 60+)
- Moving direction is connected to the camera direction.
- Using mouse movement API of pygame, so that you can control the camera by mouse.
- Adjusting moving speed on FPS to make the velocity stable.

**Todo**

- Something wrong with the covering relationship. Seems to happen often in direction Z. (Fixed: mismatch between barycentric coordinates and their corresponding vertices.)

**完成：**

- 告别opencv，使用pygame完成显示和按键检测(FPS 60 +)
- 移动方向和视角绑定
- 调用pygame鼠标检测接口实现鼠标转方向
- 根据FPS调整运动速度，保证速度稳定

**问题**

- 遮挡关系有时候有bug，似乎是z方向独有的



**v0.2	--	2026.9.7**

中文版在后面

**Performance Optimization**

- Implemented back-face culling to skip surfaces that are not visible to the camera.
- Optimized Z-buffer processing with NumPy broadcast.
- Significantly improved rendering performance from 1 FPS to 30–40 FPS at 640×480 resolution.

**优化：**

- 背面剔除（不渲染摄像头看不到的面）

- 使用Numpy实现批量处理Z-buffer

- 处理速度大幅提升，640*480分辨率下从上个版本的1帧到30~40帧