from setuptools import find_packages, setup

package_name = 'vedant_py_1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vedant',
    maintainer_email='vedant@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'simple_publisher = vedant_py_1.simple_publisher:main',
            'simple_subscriber = vedant_py_1.simple_subscriber:main',
            'simple_parameter = vedant_py_1.simple_parameter:main',
            'simple_turtlesim_kinematics = vedant_py_1.simple_turtlesim_kinematics:main',
            'simple_tf_kinematics = vedant_py_1.simple_tf_kinematics:main',
            'simple_service_server = vedant_py_1.simple_service_server:main'

        ],
    },
)
