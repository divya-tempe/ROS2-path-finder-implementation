from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ras598_assignment_2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.py')),
    # data_files=[
    #     ('share/ament_index/resource_index/packages',
    #         ['resource/' + package_name]),
    #     ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='eva',
    maintainer_email='nakumdivyaraj43@gmail.com',
    description='RAS598 Assignment 2 planner package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'planner_node = ras598_assignment_2.planner_node:main',
        ],
    },
)
