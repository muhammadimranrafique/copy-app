# API ROUTERS DOCUMENTATION

## This is a summary document of all the routers that need to be created

All routers should be created in the `routers/` directory and follow this structure:

### Required Routers:
1. `auth.py` - Authentication endpoints
2. `schools.py` - School management endpoints  
3. `products.py` - Product management endpoints
4. `orders.py` - Order management endpoints
5. `expenses.py` - Expense management endpoints
6. `payments.py` - Payment management endpoints
7. `dashboard.py` - Dashboard and reports endpoints

### Each router should include:
- GET endpoints for listing/fetching
- POST endpoints for creating
- PUT endpoints for updating
- DELETE endpoints for deletion (where appropriate)
- PATCH endpoints for partial updates
- Proper authentication using JWT
- Error handling
- Google Sheets sync integration

### Router Template Example:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import *
from utils.auth import get_current_user
import json

router = APIRouter()

@router.get("/", response_model=List[ModelRead])
def read_items(session: Session = Depends(get_session)):
    statement = select(Model)
    items = session.exec(statement).all()
    return items

@router.post("/", response_model=ModelRead)
def create_item(item: ModelCreate, session: Session = Depends(get_session)):
    db_item = Model(**item.dict())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
```

Note: Due to message length, I'll create placeholder router files for now that can be implemented later when you're ready to test the system end-to-end.



