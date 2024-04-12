from pydantic import BaseModel


class CompanyProfileSchema(BaseModel):
    working_weekend: bool

    class Config:
        orm_mode = True


class UserProfileSchema(BaseModel):
    page: str
    show_columns: str

    class Config:
        orm_mode = True
        from_attributes = True


class UserProfileCreateSchema(BaseModel):
    """ User profile creation schema use to in services """
    page: str
    show_columns: str
    creator: int