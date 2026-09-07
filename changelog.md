# 3D-Engine

**v0.2	--	2026.9.7**

中文版在后面

**Performance Optimization**

- Implemented back-face culling to skip surfaces that are not visible to the camera.
- Optimized Z-buffer processing with NumPy broadcast.
- Significantly improved rendering performance from 1 FPS to 30–40 FPS at 640×480 resolution.

**优化：**

背面剔除（不渲染摄像头看不到的面）

使用Numpy实现批量处理Z-buffer

处理速度大幅提升，640*480分辨率下从上个版本的1帧到30~40帧