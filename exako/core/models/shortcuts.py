from fastapi import HTTPException, status
from sqlalchemy import select

def get_object_or_404(Model, session, **kwargs):
    obj = session.exec(select(Model).filter_by(**kwargs)).first()
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{Model.__name__} object does not exists.',
        )
    return obj