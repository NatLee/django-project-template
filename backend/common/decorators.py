from functools import wraps
import time
from common import errorcode
from rest_framework import status as http_status
from common.helperfunc import get_request_input, api_response
from common.exceptions import RequestInputParserError
from django.conf import settings
from common.logs_writer import logswriter
from django.conf import settings



class KeyCheck:
    def __init__(self, SystemName=None, FileName='log', RemainDays=settings.LOGS_REMOVE_DAYS):
        self.logswriter_ = logswriter(SystemName=SystemName, FileName=FileName, RemainDays=RemainDays)
        
    def key_check(self, required_data=None):
        if required_data is None:
            required_data = []
        logswriter_ = self.logswriter_

        def f(func):
            @wraps(func)
            def wrapper(self, *args, **router):
                request = args[0]
                try:
                    input_data, router = get_request_input(
                        request, request.method, required_data, router
                    )
                    ret = func(self, request, input_data, router)
                except RequestInputParserError as e:
                    msg = "Request input parse error"
                    ret = api_response(
                        result=None,
                        status=http_status.HTTP_200_OK,
                        code=errorcode.INPUT_ERROR,
                        error=str(e),
                    )
                    logswriter_.write_log(f'[Error]: {self.__class__.__name__} --> {msg}')
                except Exception as e:
                    msg = "UNKNOWN ERROR"
                    logswriter_.write_log(f'[Error]: {self.__class__.__name__} --> {msg}')
                    ret = api_response(
                        result=None,
                        status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                        code=errorcode.UNKNOW_ERROR,
                        error=str(e),
                    )
                return ret

            return wrapper

        return f
    
