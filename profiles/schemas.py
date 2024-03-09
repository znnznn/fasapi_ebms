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
