from dotmap import DotMap
from app.database import get
from fastapi import Depends

_mocks: dict = {
    'db': Depends(get_db),
    'course_id': '61d21fdc00988e6ca9284474',
    'course_insertion': {'hours': 1, 'price': 87.0, 'title': 'Course updated', 'description': ''}
}
MOCKS = DotMap(_mocks)
