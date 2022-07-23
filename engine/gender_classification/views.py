import uuid
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from . tasks import *
import mimetypes
import pandas as pd
import os


@api_view(['GET'])
def index(request):
    return render(request, 'initializer.html')


@api_view(['POST', 'GET'])
def initializer(request):
    if request.method == 'POST':
        request_response_table = RequestResponse()
        request_response_table.unique_id = uuid.uuid4()
        request_response_table.request_time = datetime.datetime.now()
        if request.POST['data_type'] == 'single':
            request_response_table.request_single_data = request.POST['single_data']
            request_response_table.request_data_type = 'single'
        if request.POST['data_type'] == 'bulk':
            request_response_table.request_bulk_data = request.FILES['bulk_data']
            request_response_table.request_data_type = 'bulk'
        request_response_table.save()
        classification_task.delay()
        data = {
            'URL': f'http://127.0.0.1:8000/prediction?unique_id={request_response_table.unique_id}'
        }
        return render(request, 'initializer.html', data)
    else:
        data = {
            "status_code": 'HTTP' + status.HTTP_405_METHOD_NOT_ALLOWED,
            "message": "METHOD NOT ALLOWED"
        }
        return render(request, 'error.html', data)


@api_view(['POST', 'GET'])
def prediction(request):
    unique_id = None
    if request.method == 'POST':
        unique_id = request.POST['unique_id_input']
    elif request.method == 'GET':
        unique_id = request.query_params.get('unique_id')
    try:
        result = RequestResponse.objects.get(unique_id=unique_id)
        if result.completion_status == 'Complete':
            if result.request_data_type == 'single':
                male_probability = float(result.response_probability.split(',')[0])
                female_probability = float(result.response_probability.split(',')[1])
                data = {
                    'unique_id': unique_id,
                    'status': result.completion_status,
                    'request_type': result.request_data_type,
                    'request_data': result.request_single_data,
                    'prediction': result.response_data,
                    'male_probability': male_probability,
                    'female_probability': female_probability
                }
                return render(request, 'prediction.html', data)
            elif result.request_data_type == 'bulk':
                dataframe = pd.read_csv(os.path.join(settings.MEDIA_ROOT, result.response_data))
                number_of_names = len(dataframe)
                number_of_males = len(dataframe.loc[dataframe['GENDER'] == 'Male'])
                number_of_females = len(dataframe.loc[dataframe['GENDER'] == 'Female'])
                data = {
                    'unique_id': unique_id,
                    'status': result.completion_status,
                    'request_type': result.request_data_type,
                    'request_data': result.request_bulk_data,
                    'prediction': result.response_data,
                    'number_of_names': number_of_names,
                    'number_of_males': number_of_males,
                    'number_of_females': number_of_females
                }
                return render(request, 'prediction.html', data)
        elif result.completion_status == 'Canceled':
            data = {
                'unique_id': unique_id,
                'status': result.completion_status,
                'message': result.response_message
            }
            return render(request, 'prediction.html', data)
        elif result.completion_status == 'Pending':
            data = {
                'unique_id': unique_id,
                'status': result.completion_status,
                'message': 'We are processing your data, please come again later...!!!'
            }
            return render(request, 'prediction.html', data)
        elif result.completion_status == 'Incomplete':
            data = {
                'unique_id': unique_id,
                'status': result.completion_status,
                'message': 'Your process is in queue, it will start soon !!!'
            }
            return render(request, 'prediction.html', data)
    except Exception as e:
        data = {
            'unique_id': unique_id,
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': 'NO REQUEST FOUND'
        }
        return render(request, 'error.html', data)


def download(request, file_path):
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            mime_type, _ = mimetypes.guess_type(file_path)
            response = HttpResponse(file.read(), content_type=mime_type)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        data = {
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': f'NO FILE FOUND'
        }
        return render(request, 'error.html', data)
