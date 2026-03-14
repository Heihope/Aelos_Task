#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@说明:发布摄像头图像
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImagePublisher(Node):
    def __init__(self, name):
        super().__init__(name)
        # 创建发布者，发布原始图像话题 /image_raw
        self.publisher_ = self.create_publisher(Image, 'image_raw', 10)
        # 定时器，每0.1秒发布一帧
        self.timer = self.create_timer(0.1, self.timer_callback)
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        self.cv_bridge = CvBridge()
        self.get_logger().info('摄像头图像发布节点已启动')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # 将OpenCV图像转换为ROS Image消息并发布
            self.publisher_.publish(self.cv_bridge.cv2_to_imgmsg(frame, 'bgr8'))
            self.get_logger().info('发布一帧图像')
        else:
            self.get_logger().warn('无法获取摄像头图像')

def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher("img_pub")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
