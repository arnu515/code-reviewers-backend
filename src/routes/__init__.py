from flask import make_response, jsonify, request
from typing import Optional, Union, List, Any


class FailedRequest(Exception):
    def __init__(self, message: str, data: Optional[dict] = None, code: int = 400):
        self.message = message
        self.data = data
        self.code = code

    def dict(self):
        if self.data is None:
            self.data = {}
        return dict(message=self.message, data=self.data, success=False)

    @property
    def response(self):
        return make_response(jsonify(self.dict()), self.code)


def good_response(message: str, data: Optional[dict] = None, code: int = 200):
    if data is None:
        data = {}
    return make_response(jsonify(dict(success=True, message=message, data=data)), code)


def get_from_request(item: Union[str, List[str]], required: Union[bool, List[bool]]) -> Union[Any, List[Any]]:
    if not request.is_json:
        raise FailedRequest("Please send JSON data")

    if type(item) == list:
        required = [required for _ in range(len(item))] if type(required) == bool else required
        return [get_from_request(item[i], required[i]) for i in range(len(item))]
    else:
        item_from_request = request.json.get(item, None)
        if (item_from_request is None) and required:
            raise FailedRequest(f"Property \"{item}\" missing in request body")

        return item_from_request
