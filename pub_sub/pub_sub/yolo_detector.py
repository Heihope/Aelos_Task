#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/hoke/dev_ws/venv/lib/python3.12/site-packages')
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YoloDetector(Node):
    def __init__(self, name):
        super().__init__(name)
        self.model = YOLO('yolov8n.pt')
        self.get_logger().info('YOLO 模型加载成功')

        self.sub = self.create_subscription(
            Image, 'image_raw', self.listener_callback, 10)
        self.pub = self.create_publisher(Detection2DArray, 'yolo_detections', 10)
        # 新增：发布带标注的图像
        self.image_pub = self.create_publisher(Image, 'yolo_image', 10)

        self.cv_bridge = CvBridge()
        self.frame_count = 0
        self.process_every = 5

    def listener_callback(self, msg):
        self.frame_count += 1
        if self.frame_count % self.process_every != 0:
            return

        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'图像转换失败: {e}')
            return

        results = self.model(cv_image, verbose=False)

        # 新增：发布标注图像
        if results and len(results) > 0:
            annotated_frame = results[0].plot()
            annotated_msg = self.cv_bridge.cv2_to_imgmsg(annotated_frame, 'bgr8')
            annotated_msg.header = msg.header
            self.image_pub.publish(annotated_msg)

        detections_msg = Detection2DArray()
        detections_msg.header = msg.header

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]

                    detection = Detection2D()
                    detection.header = msg.header
                    detection.bbox.center.position.x = (x1 + x2) / 2.0
                    detection.bbox.center.position.y = (y1 + y2) / 2.0
                    detection.bbox.center.theta = 0.0
                    detection.bbox.size_x = x2 - x1
                    detection.bbox.size_y = y2 - y1

                    hypothesis = ObjectHypothesisWithPose()
                    hypothesis.hypothesis.class_id = cls_name
                    hypothesis.hypothesis.score = conf
                    detection.results.append(hypothesis)

                    detections_msg.detections.append(detection)

                    self.get_logger().info(
                        f'{cls_name}: center=({(x1+x2)/2:.1f},{(y1+y2)/2:.1f}), '
                        f'size={x2-x1:.1f}x{y2-y1:.1f}, conf={conf:.2f}'
                    )

        self.pub.publish(detections_msg)

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector('yolo_detector')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()