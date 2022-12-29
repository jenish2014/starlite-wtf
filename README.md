## WTForms Support for Starlite Framework

### Features supported :
- Create Forms
- Populate data via POST, json, python object, Query parameters
- Populate data after form creation.
- Validate data, custom validators and support for async_validators
- File uploads

### Examples :
 
```python 
    import StarliteForm
    
    class BasicForm(StarliteForm):
        firstname = StringField(name='firstname', validators=[Length(min=4, max=8)])
        lastname = StringField(name='lastname', validators=[DataRequired()])
        active = BooleanField(name='active')
    
    class FileForm(StarliteForm):
        doc = FileField(label='Test Document')
    
    
    # Create and return rendered Form 
    @get()
    async def get_empty_form(request: Request) -> Template:
        form = await BasicForm.create(request)
        return Template(name="basic_form.html", context={'form': form})
    
    
    # receive POST data, validate it and respond accordingly
    @post()
    async def populate_from_post(request: Request) -> Template:
        form = await BasicForm.create(request)
        valid = await form.validate() # OR
        valid = await from.validate_on_submit() # checks if request.method is GET
        
        if valid:
            return Template(name="success.html", context={'form': form}) 
        return Template(name="basic_form.html", context={'form': form})
    
    
    # receive file in MULTIPART encoded POST data
    @post(http_method=['GET', 'POST'])
    async def populate_from_post(request: Request) -> Template:
        form = await FileForm.create(request)
        if request.method == 'POST'
            file_data = await form.doc.data.read()
            assert form.doc.data.filename == 'starlite.txt'
            assert file_data == "b'This is a starlite test file'"
            return Template(name='success.html', context={'form': form})
        
        return Template(name="basic_form.html", context={'form': form})
```