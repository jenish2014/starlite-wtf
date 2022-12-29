import json
from dataclasses import dataclass
from io import BytesIO

from starlite import create_test_client, get, MediaType, Request, Response, post
from starlite.status_codes import HTTP_200_OK


def test_health_check():
    @get("/health-check", media_type=MediaType.TEXT)
    def health_check() -> str:
        return "healthy"

    with create_test_client(route_handlers=health_check) as client:
        response = client.get("/health-check")
        assert response.status_code == HTTP_200_OK
        assert response.text == "healthy"


def test_get_empty_form(BasicForm):
    @get()
    async def get_empty_form(request: Request) -> Response:
        form = await BasicForm.create(request)
        return Response(content=form.data)

    with create_test_client(route_handlers=get_empty_form) as client:
        response = client.get('/')
        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data['firstname'] is None
        assert response_data['lastname'] is None
        assert response_data['active'] is False


def test_populate_form_using_post_data(BasicForm):
    @post()
    async def populate_from_post(request: Request) -> Response:
        form = await BasicForm.create(request)
        return Response(content=form.data)

    with create_test_client(route_handlers=populate_from_post) as client:
        response = client.post('/',
                               data={'firstname': 'username',
                                     'lastname': 'users',
                                     'active': True})
        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data['firstname'] == 'username'
        assert response_data['lastname'] == 'users'
        assert response_data['active'] is True


def test_populate_form_using_json_data(BasicForm):
    @post()
    async def populate_from_json(request: Request) -> Response:
        form = await BasicForm.create(request)
        return Response(content=form.data)

    with create_test_client(route_handlers=populate_from_json) as client:
        response = client.post('/',
                               json=json.dumps({'firstname': 'jsons',
                                                'lastname': 'dumps',
                                                'active': True}),
                               headers={'content-type': 'application/json'}
                               )
        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data['firstname'] == 'jsons'
        assert response_data['lastname'] == 'dumps'
        assert response_data['active'] is True


def test_populate_form_after_init(BasicForm):
    @post()
    async def populate_after_init(request: Request) -> Response:
        form = BasicForm(request)
        response_data = dict()
        response_data['empty_form'] = form.data

        from src.util import get_formdata
        formdata = await get_formdata(request=request)
        form.process(formdata=formdata)
        response_data['populated_form'] = form.data

        return Response(content=response_data)

    with create_test_client(route_handlers=populate_after_init) as client:
        response = client.post('/', data={'firstname': 'user'})
        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        empty_form = response_data['empty_form']
        populated_form = response_data['populated_form']

        assert empty_form['firstname'] is None
        assert empty_form['lastname'] is None
        assert empty_form['active'] is False

        assert populated_form['firstname'] == 'user'
        assert populated_form['lastname'] is None
        assert populated_form['active'] is False


def test_populate_form_using_query_parameters(BasicForm):
    @post()
    async def populate_from_query_params(request: Request) -> Response:
        form = await BasicForm.create(request)
        return Response(content=form.data)

    with create_test_client(route_handlers=populate_from_query_params) as client:
        response = client.post('/?firstname=args')
        assert response.status_code == HTTP_200_OK
        response_data = json.loads(response.content)
        assert response_data['firstname'] == 'args'
        assert response_data['lastname'] is None
        assert response_data['active'] is False


def test_populate_form_using_object(BasicForm):
    @dataclass
    class User:
        firstname: str
        lastname: str
        active: bool

    @post()
    async def populate_from_obj(request: Request) -> Response:
        user_obj = User(firstname='Jon', lastname='Doe', active=True)
        form = await BasicForm.create(request, obj=user_obj)

        return Response(content=form.data)

    with create_test_client(route_handlers=populate_from_obj) as client:
        response = client.post('/')
        assert response.status_code == HTTP_200_OK
        form_data = response.json()

        assert form_data['firstname'] == 'Jon'
        assert form_data['lastname'] == 'Doe'

        # Default value for checkbox is False(Unchecked)
        # Value of object get overridden by formdata which in this case
        # is user_obj.active(True) -> form.active.data(False)
        assert form_data['active'] is False


def test_update_object_using_form_data(BasicForm):
    @dataclass
    class User:
        firstname: str
        lastname: str
        active: bool

    @post()
    async def update_obj(request: Request) -> Response:
        user_object = User(firstname='Jon', lastname='Doe', active=True)

        form = await BasicForm.create(request, obj=user_object)
        form.populate_obj(user_object)

        return Response(content=(form.data, user_object))

    with create_test_client(route_handlers=update_obj) as client:
        response = client.post('/', data={'firstname': 'Jane', 'active': False})

        assert response.status_code == HTTP_200_OK
        form_data, user_obj = response.json()

        assert form_data['firstname'] == 'Jane'
        assert form_data['lastname'] == 'Doe'
        assert form_data['active'] is False

        assert user_obj['firstname'] == 'Jane'
        assert user_obj['lastname'] == 'Doe'
        assert user_obj['active'] is False


def test_file_upload(FileForm):
    @post()
    async def upload_file(request: Request) -> Response:
        form = await FileForm.create(request)
        response_data = dict()
        response_data['filename'] = form.doc.data.filename
        response_data['filedata'] = str(await form.doc.data.read())
        return Response(content=response_data)

    f = BytesIO(b'This is a starlite test file')
    f.name = 'starlite.txt'
    with create_test_client(route_handlers=upload_file) as client:
        response = client.post('/', files={'doc': f})
        assert response.status_code == HTTP_200_OK
        formdata = response.json()

        assert formdata['filename'] == 'starlite.txt'
        assert formdata['filedata'] == "b'This is a starlite test file'"
