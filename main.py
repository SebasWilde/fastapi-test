from typing import Optional
from enum import Enum
from fastapi import (
    FastAPI,
    Body,
    Query,
    Path,
    status,
    Form,
    Header,
    Cookie,
    File,
    UploadFile,
    HTTPException,
)
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()


# Models
class HariColor(Enum):
    white = "White"
    red = "Red"


class PersonBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., gt=0, le=100)
    hair_color: Optional[HariColor] = Field(default=None)
    is_married: Optional[bool] = Field(default=None)


class Person(PersonBase):
    password: str = Field(..., min_length=8)

    # class Config:
    #     schema_extra = {
    #         'example': {
    #             'first_name': 'Sebastian',
    #             'last_name': 'Alarcón',
    #             'age': 26,
    #             'hair_color': HariColor.red,
    #             'is_married': False,
    #             'password': 'password',
    #         }
    #     }


class PersonOut(Person):
    ...


class Location(BaseModel):
    city: str
    state: str
    country: str


class LoginOut(BaseModel):
    username: str = Field(..., max_length=20)


@app.get(path='/', status_code=status.HTTP_200_OK)
def home():
    return {'Hello': 'World'}


@app.post(
    path='/person/new',
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
    tags=['Persons'],
    summary='Create new person'
)
def create_person(person: Person = Body(...)):
    """
    Create a new person
    :param person: person data
    :return: person instance
    """

    return person


@app.get('/person/detail', tags=['Persons'])
def show_person(
    name: Optional[str] = Query(None, min_length=1, max_length=50),
    age: int = Query(...),
):
    return {'name': name, 'age': age}


persons = [1, 2, 3, 4, 5]


@app.get('/person/detail/{person_id}', tags=['Persons'])
def show_person(person_id: int = Path(..., gt=0)):
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Person does not exists',
        )
    return {'person_id': 'Exists'}


@app.put('/person/{person_id}', tags=['Persons'])
def update_person(
    person_id: int = Path(..., gt=0, title='Person ID'),
    person: Person = Body(...),
    location: Location = Body(...),
):
    results = person.dict()
    results.update(location.dict())
    return results


@app.post(
    path='/login',
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    tags=['Auth'],
)
def login(username: str = Form(...), password: str = Form(...)):
    return LoginOut(username=username).dict()


# Cookies and headers
@app.post(path='/contact', status_code=status.HTTP_200_OK)
def contact(
    first_name: str = Form(..., max_length=20, min_length=1),
    last_name: str = Form(..., max_length=20, min_length=1),
    email: EmailStr = Form(...),
    message: str = Form(..., min_length=20),
    user_agent: Optional[str] = Header(None),
    ads: Optional[str] = Cookie(None),
):
    return user_agent


# Images
@app.post(path='/post-image')
def post_image(image: UploadFile = File(...)):
    return {
        'filename': image.filename,
        'format': image.content_type,
        'size (kb)': round(image.file.read().__len__() / 1024, ndigits=2),
    }
