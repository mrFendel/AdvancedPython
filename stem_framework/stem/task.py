"""
Tasks:
    Depending on task definition and input metadata, the system calculates an acyclic
dependency graph of tasks and data. Task dependency is represented by the name of task and
metadata passed to the task (task could modify metadata passed to dependencies), so each task
calculates its dependencies recursively. Data dependencies consist only of data name or mask.
Task and data are resolved by the workspace by name. Task graph is checked for cycles.

"""