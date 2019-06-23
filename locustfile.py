from locust import HttpLocust, TaskSet, task


class UserActions(TaskSet):
    @task(1)
    def list(self):
        self.client.get('/mediation/backends/')


class ApplicationUser(HttpLocust):
    task_set = UserActions
    min_wait = 0
    max_wait = 0
