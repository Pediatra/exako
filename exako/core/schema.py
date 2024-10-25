from fastapi import status

OBJECT_NOT_FOUND = {
    status.HTTP_404_NOT_FOUND: {
        'content': {'application/json': {'example': {'detail': 'object not found.'}}},
    },
}

PERMISSION_DENIED = {
    status.HTTP_401_UNAUTHORIZED: {
        'content': {
            'application/json': {'example': {'detail': 'invalid credentials.'}}
        },
    },
    status.HTTP_403_FORBIDDEN: {
        'content': {
            'application/json': {'example': {'detail': 'not enough permissions.'}}
        },
    },
}
