# models/phish_event.py
from datetime import datetime
import uuid
from sqlalchemy import func, Date, cast
from extensions import db


class PhishEvent(db.Model):
    """Model to track phishing link clicks and user interactions"""
    
    __tablename__ = "phish_events"
    
    # Primary key with UUID
    id = db.Column(
        db.UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )

    # User information
    sent_by = db.Column(
        db.String(255), 
        nullable=False, 
        index=True
    )
    
    # User information
    email = db.Column(
        db.String(255), 
        nullable=False, 
        index=True
    )
    
    # Request information
    ip_address = db.Column(
        db.String(45),  # Supports IPv6
        nullable=False
    )
    
    user_agent = db.Column(
        db.Text, 
        nullable=False
    )
    
    # Phishing campaign information
    link_hash = db.Column(
        db.String(64), 
        nullable=False, 
        index=True
    )
    
    campaign_id = db.Column(
        db.String(64),
        nullable=True,
        index=True
    )
    
    # Additional metadata
    referer = db.Column(
        db.Text,
        nullable=True
    )
    
    device_type = db.Column(
        db.String(50),  # mobile, desktop, tablet
        nullable=True
    )
    
    browser = db.Column(
        db.String(50),
        nullable=True
    )
    
    os = db.Column(
        db.String(50),
        nullable=True
    )
    
    # Geolocation (optional)
    country = db.Column(
        db.String(2),  # ISO country code
        nullable=True
    )
    
    city = db.Column(
        db.String(100),
        nullable=True
    )
    
    # Timestamps
    clicked_at = db.Column(
        db.DateTime(timezone=True), 
        default=func.now(),
        nullable=False,
        index=True
    )
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_email_campaign', 'email', 'campaign_id'),
    )
    
    def __repr__(self):
        return f'<PhishEvent {self.id}: {self.email} @ {self.clicked_at}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'email': self.email,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'link_hash': self.link_hash,
            'campaign_id': self.campaign_id,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'country': self.country,
            'city': self.city,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None
        }
    
    @classmethod
    def get_stats_by_campaign(cls, campaign_id):
        """Get statistics for a specific campaign"""
        return db.session.query(
            func.count(cls.id).label('total_clicks'),
            func.count(func.distinct(cls.email)).label('unique_users'),
            func.count(func.distinct(cls.ip_address)).label('unique_ips'),
            func.min(cls.clicked_at).label('first_click'),
            func.max(cls.clicked_at).label('last_click')
        ).filter(cls.campaign_id == campaign_id).first()
    
    @classmethod
    def get_clicks_by_date(cls, start_date=None, end_date=None):
        """Get click counts grouped by date"""
        query = db.session.query(
            func.date(cls.clicked_at).label('date'),
            func.count(cls.id).label('clicks')
        )
        
        if start_date:
            query = query.filter(cls.clicked_at >= start_date)
        if end_date:
            query = query.filter(cls.clicked_at <= end_date)
            
        return query.group_by(func.date(cls.clicked_at)).all()
    
    @classmethod
    def get_top_browsers(cls, limit=10):
        """Get top browsers by click count"""
        return db.session.query(
            cls.browser,
            func.count(cls.id).label('count')
        ).filter(
            cls.browser.isnot(None)
        ).group_by(
            cls.browser
        ).order_by(
            func.count(cls.id).desc()
        ).limit(limit).all()


# models/phish_campaign.py
class PhishCampaign(db.Model):
    """Model to manage phishing campaigns"""
    
    __tablename__ = "phish_campaigns"
    
    id = db.Column(
        db.String(64),
        primary_key=True,
        default=lambda: uuid.uuid4().hex
    )
    
    name = db.Column(
        db.String(255),
        nullable=False
    )
    
    description = db.Column(
        db.Text,
        nullable=True
    )
    
    target_url = db.Column(
        db.String(500),
        nullable=False
    )
    
    created_by = db.Column(
        db.String(255),
        nullable=False
    )
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    
    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )
    
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )
    
    # Relationship with events
    events = db.relationship(
        'PhishEvent',
        backref='campaign',
        lazy='dynamic',
        foreign_keys='PhishEvent.campaign_id',
        primaryjoin='PhishCampaign.id == PhishEvent.campaign_id'
    )