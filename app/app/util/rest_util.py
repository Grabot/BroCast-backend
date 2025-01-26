from fastapi import Response, status


def get_failed_response(message, response: Response):
    # It's a failed response, but the response itself is fine
    response.status_code = status.HTTP_200_OK
    actual_response = {
        "result": False,
        "message": message,
    }
    return actual_response
