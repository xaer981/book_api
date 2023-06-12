from fastapi_pagination import Page
from pydantic import Field

CustomPage = Page.with_custom_options(size=Field(default=5, ge=1, le=10))
