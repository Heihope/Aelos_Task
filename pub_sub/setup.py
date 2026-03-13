from setuptools import setup
import os
from glob import glob

package_name = 'pub_sub'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Image processing package for red object detection',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'img_pub = pub_sub.img_pub:main',
            'img_sub = pub_sub.img_sub:main',
            'yolo_detector = pub_sub.yolo_detector:main',
        ],
    },
)
