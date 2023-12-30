from osbot_aws.aws.ecs.ECS_Fargate_Task import ECS_Fargate_Task


class Temp_ECS_Fargate_Task:
    def __init__(self, image_name, delete_on_exit=False):
        cluster_name        = f'Temp_ECS_Fargate_Task-{image_name}'
        self.delete_on_exit = delete_on_exit
        self.fargate_task   = ECS_Fargate_Task(cluster_name=cluster_name, image_name=image_name)

    def __enter__(self):
        self.fargate_task.setup()
        return self.fargate_task

    def __exit__(self, exception_type, exception_value, traceback):
        if self.delete_on_exit:
            self.fargate_task.delete_cluster_task_definition_tasks_roles()