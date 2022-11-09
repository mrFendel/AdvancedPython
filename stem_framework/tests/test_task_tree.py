from unittest import TestCase

from stem_framework.stem.task_tree import TaskTree
from .example_task import int_range, int_scale


class TaskTreeTest(TestCase):
    def setUp(self) -> None:
        self.task_node = TaskTree.build_node(int_scale)

    def test_task_tree(self):
        self.assertEqual(self.task_node.dependencies[0].task, int_range)
