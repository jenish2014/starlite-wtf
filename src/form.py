from starlite import Request, FormMultiDict
from starlite.datastructures import MultiDict
from wtforms import Form

from .util import get_formdata, patch_FormMultiDict

SUBMIT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


class StarliteForm(Form):
    def __init__(self, request, *args, **kwargs):
        self._request = request
        super().__init__(*args, **kwargs)

    @classmethod
    async def create(cls, request: Request, **kwargs) -> Form:
        if request.method in SUBMIT_METHODS:
            formdata = await get_formdata(request)
            if request.content_type[0] == 'application/json':
                return cls(request, data=formdata, **kwargs)
            else:
                return cls(request, formdata=formdata, **kwargs)

        return cls(request, **kwargs)
