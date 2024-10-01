# todo: see if this is still needed
# from osbot_utils.utils.Process import Process
#
#
# class Lambda_Docker:
#
#     def __init__(self):
#         self.docker_image = "lambci/lambda:python3.8"
#
#
#     def run_bash(self, cmd):
#         run_params = ["run", "--rm", "--entrypoint", "bash", self.docker_image, "-c",cmd]
#         return Process.run("docker", run_params)
#
#     # todo: finish this method
#     # def invoke(self, cmd):
#     #     run_params = ["run", "--rm",
#     #                   "--entrypoint", "bash",
#     #                   self.docker_image, "-c", cmd]
#     #     # docker run --rm                             \
#
#         #           -v "$PWD":/var/task:ro,delegated \
#         #           lambci/lambda:python3.8          \
#         #           lambda_function.run
#
