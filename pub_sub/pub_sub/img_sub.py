#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@说明: ROS2话题示例-订阅图像，检测红色物体并发布处理后图像
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

# 红色HSV阈值
# 根据实际光线和颜色微调S和V的下限
lower_red1 = np.array([0, 150, 150])     # 范围1：H 0~10
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([172, 150, 150])   # 范围2：H 160~180
upper_red2 = np.array([180, 255, 255])

class ImageSubscriber(Node):
    def __init__(self, name):
        super().__init__(name)
        # 订阅原始图像话题
        self.sub = self.create_subscription(
            Image, 'image_raw', self.listener_callback, 10)
        # 发布处理后的图像话题
        self.publisher_ = self.create_publisher(Image, 'image_processed', 10)
        self.cv_bridge = CvBridge()
        self.get_logger().info('图像处理节点已启动，等待图像...')

    def object_detect(self, image):
        """检测红色物体，绘制边界框和中心点，并返回处理后的图像"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 生成两个红色范围的掩码并合并
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        for cnt in contours:
            if cnt.shape[0] < 150:   # 过滤太小轮廓
                continue

            # 获取边界框
            x, y, w, h = cv2.boundingRect(cnt)
            # 计算中心点
            cx = x + w // 2
            cy = y + h // 2

            # 在图像上绘制
            cv2.drawContours(image, [cnt], -1, (0, 255, 0), 2)          # 绿色轮廓
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2) # 蓝色矩形框
            cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)              # 红色中心点

            # 打印物体信息
            self.get_logger().info(
                f'检测到物体: 中心=({cx},{cy}), 宽度={w}, 高度={h}'
            )

        # 显示处理结果（窗口名 Processed Image）
        cv2.imshow("Processed Image", image)
        cv2.waitKey(1)

        return image

    def listener_callback(self, data):
        # 将ROS图像转为OpenCV格式
        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(data, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'图像转换失败: {e}')
            return

        # 进行物体检测并获取处理后的图像
        processed_image = self.object_detect(cv_image)

        # 将处理后的OpenCV图像转回ROS消息并发布
        try:
            ros_image = self.cv_bridge.cv2_to_imgmsg(processed_image, 'bgr8')
            self.publisher_.publish(ros_image)
            self.get_logger().info('已发布处理后的图像')
        except Exception as e:
            self.get_logger().error(f'发布失败: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber("img_sub")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()