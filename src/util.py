import json
import types
from typing import List, TypeVar, Any

from starlite import FormMultiDict
from starlite.datastructures import MultiDict

T = TypeVar('T')


def getlist(self, key: str) -> List[T]:
    return self.getall(key, [])


def patch_FormMultiDict(formdata):
    # getlist method on FormMultiDict is deprecated
    # Until removed, patch getlist method
    if isinstance(formdata, FormMultiDict) and hasattr(formdata, 'getlist'):
        formdata.getlist = types.MethodType(getlist, formdata)
    if isinstance(formdata, MultiDict) and hasattr(formdata, 'getlist'):
        formdata.getlist = types.MethodType(getlist, formdata)
    return formdata


async def get_formdata(request=None, data: dict[str, Any] = None):
    if request is None and data is not None:
        return patch_FormMultiDict(FormMultiDict(data))

    if request.content_type[0] == 'application/json':
        # in some instances request.json() returns string instead of dict
        # this checks for string and returns MultiDict out of it.
        json_data = await request.json()
        if isinstance(json_data, str):
            return patch_FormMultiDict(MultiDict(json.loads(json_data)))
        return patch_FormMultiDict(json_data)
    elif request.query_params:
        return patch_FormMultiDict(request.query_params)
    else:
        formdata = await request.form()
        return patch_FormMultiDict(formdata)
