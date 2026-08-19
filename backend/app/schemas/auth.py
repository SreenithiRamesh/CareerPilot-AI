from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=255,
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse