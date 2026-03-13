# Aelos任务提交

## 项目结构说明
本仓库包含三个 ROS2 包，分别对应三次任务：
- `camera_catch_redball`：任务1 – 红色小球检测（静态图片）
- `pub_sub`：任务2 – 红色物体检测与图像发布订阅（实时视频）
- `pub_sub`：任务3 – YOLO 通用目标检测（实时视频，坐标发布）

---

## 任务1：红色小球检测（静态图片）

### 功能描述
- 使用 OpenCV 读取本地图片 `redball.png`
- 将图像转换到 HSV 颜色空间，通过两个红色阈值范围（0~10 和 170~180）生成掩码，合并后提取红色区域。这样做因为在HSV色相环中红色位于两端（0°附近和180°附近），单个连续范围会包含中间的非红色（如黄色、绿色），而两个范围能完整覆盖所有红色调，同时有效排除干扰色。
- 检测轮廓，过滤面积较小的噪声，绘制矩形框和中心点，并在图像上标注中心坐标。
- 在终端输出红色小球的中心坐标和尺寸信息。

### 代码位置
- 完整 ROS2 包：`camera_catch_redball/`
- 核心脚本：`camera_catch_redball/redball.py`

### 运行方法
1. **编译包**（在工作空间中）
   ```bash
   cd ~/dev_ws
   colcon build --packages-select camera_catch_redball
   source install/setup.sh
2. **运行**
   ros2 run camera_catch_redball redball
   
## 任务2：红色物体检测与图像发布订阅（实时视频）

### 功能描述
- **`img_pub.py`**：通过 OpenCV 打开摄像头（设备 `/dev/video0`），以 10 Hz 的频率发布原始图像到话题 `/image_raw`（使用 `sensor_msgs/Image` 消息）。
- **`img_sub.py`**：订阅 `/image_raw`，将图像转换为 OpenCV 格式，在 HSV 空间中使用两个红色阈值范围（0~10 和 172~180）生成掩码，合并后检测红色区域。对检测到的轮廓进行筛选（过滤面积小于150像素的噪声），绘制绿色轮廓、蓝色矩形框和红色中心点，并在终端输出物体的中心坐标及尺寸。处理后的图像通过话题 `/image_processed` 发布，同时使用 `cv2.imshow` 显示处理结果（窗口名 `Processed Image`）。

### 代码位置
- 完整 ROS2 包：`pub_sub/`
- 核心脚本：`pub_sub/img_pub.py` 和 `pub_sub/img_sub.py`

### 运行方法
1. **编译包**（在工作空间中）
   ```bash
   cd ~/dev_ws
   colcon build
   source install/setup.sh
2. **运行**
   ros2 run pub_sub img_pub
   ros2 run pub_sub img_sub
   rqt_image_view(在话题列表中选择 /image_processed 即可看到带标注的画面。)

## 任务3：YOLO 通用目标检测（实时视频）

### 功能描述
- **`yolo_detector.py`**：订阅摄像头原始图像话题 `/image_raw`，使用 YOLOv8 预训练模型（`yolov8n.pt`）进行实时目标检测。
- 检测结果包括物体的类别、置信度、边界框中心坐标（像素）及尺寸，通过话题 `/yolo_detections` 发布（消息类型 `vision_msgs/Detection2DArray`）。
- 同时发布带标注的图像到话题 `/yolo_image`，可在 `rqt_image_view` 中实时查看检测框和标签。
- 节点每 5 帧处理一次图像，以降低 CPU 负载（可通过修改 `self.process_every` 调整）。

### 代码位置
- 完整 ROS2 包：`pub_sub/`
- 核心脚本：`pub_sub/yolo_detector.py`

### 运行方法
1. **确保依赖安装**  
   本节点需要 `ultralytics` 库，建议在虚拟环境中安装（已在代码中通过 `sys.path.insert` 指定路径，如需修改请调整）。安装命令：
   ```bash
   pip install ultralytics   
2. **编译包**
   cd ~/dev_ws
   colcon build
   source install/setup.sh
3. **运行 节点**
   ros2 run pub_sub img_pub
   ros2 run pub_sub yolo_detector
4. **查看检测结果**
   ros2 topic echo /yolo_detections
   rqt_image_view
