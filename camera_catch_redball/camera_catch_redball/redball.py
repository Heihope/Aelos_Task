#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@参考: 古月居(www.guyuehome.com) 苹果检测代码
@说明: ROS2节点示例-通过颜色识别检测图片中的红色小球，框选并输出坐标
"""

import os
import rclpy
from rclpy.node import Node
import cv2
import numpy as np

def detect_red_ball(image):
    """
    在图像中检测红色小球，绘制框和中心点，并输出坐标信息
    """
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义红色的两个HSV范围（覆盖红色在色环两端的区域）
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # 合并两个掩码
    mask = cv2.bitwise_or(mask1, mask2)

    # 查找轮廓（只检测最外层，使用简单近似）
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # 过滤面积较小的噪声
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2

            # 绘制矩形框（绿色）
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 绘制中心点（红色实心圆）
            cv2.circle(image, (cx, cy), 3, (0, 0, 255), -1)
            # 标注中心坐标（绿色文字）
            cv2.putText(image, f"Center: ({cx}, {cy})", (cx, cy - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 输出坐标信息到终端
            print(f"红色小球中心坐标: (x={cx}, y={cy}, width={w}, height={h})")

    # 显示结果图像
    cv2.imshow("Red Ball Detection", image)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()


def main(args=None):
    # ROS2节点初始化
    rclpy.init(args=args)
    node = Node("red_ball_detector")
    node.get_logger().info("红色小球检测节点已启动")

    # 获取脚本所在目录，构造图片路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "redball.png")

    # 检查图片是否存在
    if not os.path.exists(image_path):
        node.get_logger().error(f"图片不存在：{image_path}")
        rclpy.shutdown()
        return

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        node.get_logger().error("无法读取图像，请检查图片格式")
        rclpy.shutdown()
        return

    # 执行检测
    detect_red_ball(image)

    # 关闭ROS2
    rclpy.shutdown()


if __name__ == "__main__":
    main()
