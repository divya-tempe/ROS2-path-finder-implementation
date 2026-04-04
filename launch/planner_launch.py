from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch description for the planner package.

    This starts the planner node from ras598_assignment_2.
    """
    return LaunchDescription([
        Node(
            package='ras598_assignment_2',
            executable='planner_node',
            name='planner_node',
            output='screen'
        )
    ])