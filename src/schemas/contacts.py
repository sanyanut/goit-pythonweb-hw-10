from datetime import date, datetime
from typing import Optional, Annotated, Union

import phonenumbers
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

E164NumberType = Annotated[
    Union[str, phonenumbers.PhoneNumber], PhoneNumberValidator(number_format="E164")
]


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: E164NumberType
    birth_date: date
    additional_data: Optional[str] = Field(default=None, max_length=256)


class ContactModel(ContactBase):
    pass


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: str | None = Field(max_length=50, default=None)
    last_name: str | None = Field(max_length=50, default=None)
    email: EmailStr | None = None
    phone: E164NumberType | None = None
    birth_date: date | None = None
    additional_data: Optional[str] | None = Field(default=None, max_length=256)


class ContactResponse(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
