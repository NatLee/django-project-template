from rest_framework.response import Response
from rest_framework import status as http_status
from common import errorcode
from common.exceptions import RequestInputParserError
import math


def api_response(result=None, status=http_status.HTTP_200_OK, code=errorcode.OK, error=None, **kwargs):
    """
    Function to standardize API responses.
    """
    if not isinstance(result, list):
        result = [] if result is None else [result]

    content = {'result': result, 'code': code}

    if error is not None:
        content['message'] = error

    return Response(content, status=status, content_type="application/json", **kwargs)

def get_request_input(request, method="POST", required_data=[], router={}):
    """
    Function to parse input from an HTTP request.
    """
    input_data = dict(request.query_params if method == "GET" else request.data)

    # Flatten single-item lists for all input data
    for key, value in input_data.items():
        if isinstance(value, list) and len(value) == 1:
            input_data[key] = value[0]

    # Check for required data
    missing_data = [item for item in required_data if item not in input_data]
    if missing_data:
        raise RequestInputParserError(f"Required data not found: {', '.join(missing_data)}")

    return input_data, router

def page_helper(page, limit_by_page, data_count):
    """
    Helper function for pagination.
    
    para:
        - page : 第幾頁
        - limit_by_page : 一頁限制回傳?筆
        - data_count : 資料總比數
    return:
        - page :第幾頁
        - page_total : 總頁數
        - start : 陣列開始
        - end :陣列結束

    """
    page = max(page, 1)
    start = (page - 1) * limit_by_page
    end = start + limit_by_page
    page_total = math.ceil(data_count / limit_by_page)

    return page, page_total, start, end