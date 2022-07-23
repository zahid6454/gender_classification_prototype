from django.db import models


class RequestResponse(models.Model):
    unique_id = models.CharField(primary_key=True, max_length=40)
    request_time = models.DateTimeField()
    response_time = models.DateTimeField(default=None, null=True)
    request_data_type = models.CharField(max_length=10, null=False)
    request_single_data = models.CharField(default=None, max_length=500, null=True)
    request_bulk_data = models.FileField(default=None, null=True)
    response_data = models.CharField(default=None, max_length=500, null=True)
    response_probability = models.CharField(default=None, max_length=500, null=True)
    response_status_code = models.CharField(default=None, max_length=10, null=True)
    response_message = models.CharField(default=None, max_length=500, null=True)
    completion_status = models.CharField(default='Incomplete', max_length=20, null=False)

    def __str__(self):
        return self.unique_id
