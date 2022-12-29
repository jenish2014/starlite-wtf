import asyncio

from starlite import Request, FormMultiDict
from starlite.datastructures import MultiDict
from wtforms import Form, ValidationError

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

    def is_submitted(self):
        """Consider the form submitted if there is an active request and
        the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        """
        return self._request.method in SUBMIT_METHODS

    async def _validate_async(self, validator, field):
        """Execute async validator
        """
        try:
            await validator(self, field)
        except ValidationError as e:
            field.errors.append(e.args[0])
            return False
        return True

    async def validate(self, extra_validators=None) -> bool:
        if extra_validators is not None:
            extra = extra_validators.copy()
        else:
            extra = {}

        async_validators = {}

        # use extra validators to check for StopValidation errors
        completed = []

        def record_status(form, field):
            completed.append(field.name)

        for name, field in self._fields.items():
            func = getattr(self.__class__, f"async_validate_{name}", None)
            if func:
                async_validators[name] = (func, field)
                extra.setdefault(name, []).append(record_status)

        # execute non-async validators
        success = super().validate(extra_validators=extra)

        # execute async validators
        tasks = [self._validate_async(*async_validators[name]) for name in completed]
        async_results = await asyncio.gather(*tasks)

        # check results
        if False in async_results:
            success = False

        return success

    async def validate_on_submit(self, extra_validators=None):
        """Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return self.is_submitted() and await self.validate(extra_validators=extra_validators)
