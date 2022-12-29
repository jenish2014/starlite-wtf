from starlite import get, MediaType, create_test_client, Request, Response, route, post
from starlite.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED


def test_health_check():
    @get("/health-check", media_type=MediaType.TEXT)
    def health_check() -> str:
        return "healthy"

    with create_test_client(route_handlers=health_check) as client:
        response = client.get("/health-check")
        assert response.status_code == HTTP_200_OK
        assert response.text == "healthy"


def test_is_submitted(BasicForm):
    @route(http_method=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    async def submitted(request: Request) -> Response:
        form = await BasicForm.create(request)
        result = str(form.is_submitted())
        return Response(content=result)

    with create_test_client(route_handlers=submitted) as client:
        assert client.get('/').text == '"False"'
        assert client.post('/').text == '"True"'
        assert client.put('/').text == '"True"'
        assert client.patch('/').text == '"True"'
        assert client.delete('/').text == '"True"'


def test_validate_form(ValidateForm):
    @post()
    async def validate_form_data(request: Request) -> Response:
        form = await ValidateForm.create(request)
        valid = await form.validate()
        if valid:
            return Response(content=valid, status_code=201)
        return Response(content=valid, status_code=400)

    with create_test_client(route_handlers=validate_form_data) as client:
        response = client.post('/', data={'firstname': 'Jon', 'lastname': ''})
        assert response.status_code == HTTP_400_BAD_REQUEST

        response = client.post('/', data={'firstname': 'Jane', 'lastname': None})
        assert response.status_code == HTTP_400_BAD_REQUEST

        response = client.post('/', data={'firstname': 'Jane', 'lastname': 'Doe'})
        assert response.status_code == HTTP_201_CREATED


def test_manual_populate_and_validate(ValidateForm):
    @post()
    async def populate_manually(request: Request) -> Response:
        from src.util import get_formdata
        formdata = await get_formdata(data={'firstname': 'username'})

        # Create Form by passing FormMultiDict data to Form.__init__() instead of create constructor
        # Data passed in POST request will be ignored
        form = ValidateForm(request, formdata=formdata)
        assert form.firstname.data == 'username'
        response_data = {'before': form.data}

        # validate and check value again
        await form.validate()
        assert form.firstname.data == 'username'
        response_data['after'] = form.data
        response_data['errors'] = form.errors

        return Response(content=response_data)

    with create_test_client(route_handlers=populate_manually) as client:
        response = client.post('/', data={'firstname': 'first'})
        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data['after'] == {'firstname': 'username', 'lastname': None}
        assert response_data['before'] == response_data['after']
        assert response_data['errors']['lastname'][0] == 'This field is required.'


def test_validate_on_submit(ValidateForm):
    @route(http_method=['GET', 'POST'])
    async def validate_onsubmit(request: Request) -> Response:
        form = await ValidateForm.create(request)
        valid = await form.validate_on_submit()
        return Response(content=(form.errors, valid))

    with create_test_client(route_handlers=validate_onsubmit) as client:
        # test is_submitted() == False
        response = client.get('/')
        errors, valid = response.json()
        assert errors == {}
        assert valid is False

        # Checks for field in errors
        # test is_submitted() == True and validate() == False
        # lastname[required] firstname[length between 4 and 8]
        response = client.post('/')
        errors, valid = response.json()
        assert errors['firstname'][0] == 'Field must be between 4 and 8 characters long.'
        assert errors['lastname'][0] == 'This field is required.'
        assert valid is False

        # test is_submitted() == True and validate() == True
        response = client.post('/', data={'firstname': 'firstname'})
        errors, valid = response.json()
        assert errors['firstname'][0] == 'Field must be between 4 and 8 characters long.'
        assert errors['lastname'][0] == 'This field is required.'
        assert valid is False

        # test is_submitted() == True and validate() == True
        response = client.post('/', data={'firstname': 'Jane', 'lastname': 'Doe'})
        errors, valid = response.json()
        assert errors == {}
        assert valid is True
