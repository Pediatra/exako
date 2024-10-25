from fastapi_pagination import Page
from fastapi_pagination.customization import (
    CustomizedPage,
    UseIncludeTotal,
    UseModelConfig,
)

Page = CustomizedPage[
    Page,
    UseIncludeTotal(True),
    UseModelConfig(extra='allow'),
]
