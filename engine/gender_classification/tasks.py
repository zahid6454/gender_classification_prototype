from __future__ import absolute_import, unicode_literals
from celery import shared_task
import datetime
from . services import Service
from . models import RequestResponse


@shared_task(name="classification_task")
def classification_task():
    service = Service()
    results_single = RequestResponse.objects.filter(request_data_type='single', completion_status='Incomplete')
    for data in results_single:
        data.completion_status = 'Pending'
        data.save()
        prediction_outcome = service.classification(data.request_single_data, data.request_data_type)
        if prediction_outcome['status_code'] == 200:
            data.response_time = datetime.datetime.now()
            data.response_data = prediction_outcome['prediction'][0]
            data.response_probability = prediction_outcome['probability'][0]
            data.response_status_code = prediction_outcome['status_code']
            data.response_message = prediction_outcome['message']
            data.completion_status = 'Complete'
            data.save()
        else:
            data.response_time = datetime.datetime.now()
            data.response_status_code = prediction_outcome['status_code']
            data.response_message = prediction_outcome['message']
            data.completion_status = 'Canceled'
            data.save()

    results_bulk = RequestResponse.objects.filter(request_data_type='bulk', completion_status='Incomplete')

    for data in results_bulk:
        data.completion_status = 'Pending'
        data.save()
        prediction_outcome = service.classification(data.request_bulk_data, data.request_data_type)
        if prediction_outcome['status_code'] == 200:
            df = prediction_outcome['dataframe']
            probability = prediction_outcome['probability']
            df['GENDER'] = prediction_outcome['prediction']
            male_probability, female_probability = [], []
            for row in probability:
                male_probability.append(row.split(',')[0])
                female_probability.append(row.split(',')[1])
            df['MALE_PROBABILITY'] = male_probability
            df['FEMALE_PROBABILITY'] = female_probability
            df.to_csv(data.request_bulk_data.path, index=False)
            data.response_time = datetime.datetime.now()
            file_path = data.request_bulk_data.path.split('\\')[-1]
            data.response_data = file_path
            data.response_status_code = prediction_outcome['status_code']
            data.response_message = prediction_outcome['message']
            data.completion_status = 'Complete'
            data.save()
        else:
            data.response_time = datetime.datetime.now()
            data.response_status_code = prediction_outcome['status_code']
            data.response_message = prediction_outcome['message']
            data.completion_status = 'Canceled'
            data.save()
    return None
