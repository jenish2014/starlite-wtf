from dataclasses import dataclass

import pytest
from wtforms import StringField, FileField, BooleanField
from wtforms.validators import Length, DataRequired

from src.form import StarliteForm


@pytest.fixture
def BasicForm():
    class BasicForm(StarliteForm):
        firstname = StringField(name='firstname')
        lastname = StringField(name='lastname')
        active = BooleanField(name='active')

    return BasicForm


@pytest.fixture
def ValidateForm():
    class ValidateForm(StarliteForm):
        firstname = StringField(validators=[Length(min=4, max=8)])
        lastname = StringField(validators=[DataRequired()])

    return ValidateForm


@pytest.fixture
def FileForm():
    class FileForm(StarliteForm):
        doc = FileField(label='Test Document')

    return FileForm


@pytest.fixture
def User():
    @dataclass
    class User:
        firstname: str
        lastname: str
        active: bool

    return User
