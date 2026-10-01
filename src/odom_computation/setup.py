import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'odom_computation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rahul',
    maintainer_email='rahulrajak6942@gmail.com',
    description='Odometry computation from wheel encoder ticks for differential drive robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_node = odom_computation.odom_node:main',
            'imu_publisher = odom_computation.imu_publisher:main',
        ],
    },
)
