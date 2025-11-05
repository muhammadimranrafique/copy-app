from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
from models import Settings, SettingsUpdate, SettingsRead
from database import get_session
from utils.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])

def get_or_create_settings(session: Session) -> Settings:
    """Get existing settings or create default ones"""
    statement = select(Settings)
    settings = session.exec(statement).first()
    
    if not settings:
        settings = Settings()
        session.add(settings)
        session.commit()
        session.refresh(settings)
    
    return settings

@router.get("/", response_model=SettingsRead)
async def get_settings(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Get current application settings"""
    settings = get_or_create_settings(session)
    return settings

@router.put("/", response_model=SettingsRead)
async def update_settings(
    settings_update: SettingsUpdate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Update application settings"""
    settings = get_or_create_settings(session)
    
    # Update only provided fields
    update_data = settings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    settings.updated_at = datetime.utcnow()
    
    session.add(settings)
    session.commit()
    session.refresh(settings)
    
    return settings
