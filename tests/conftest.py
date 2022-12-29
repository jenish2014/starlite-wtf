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
def ValidationForm():
    class ValidationForm(StarliteForm):
        firstname = StringField(validators=[Length(min=3, max=8)])
        lastname = StringField(validators=[DataRequired()])

    return ValidationForm


@pytest.fixture
def FileForm():
    class FileForm(StarliteForm):
        doc = FileField(label='Test Document')

    return FileForm
