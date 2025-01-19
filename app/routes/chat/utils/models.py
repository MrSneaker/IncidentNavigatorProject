from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import datetime
from uuid import uuid4
from typing import List

from ... import db

def get_uuid():
    """Generate a unique hexadecimal UUID."""
    return uuid4().hex

class Ticket(db.Model):
    """
    Model representing support tickets associated with messages.
    
    Contains information about accidents/events including type, industry,
    and reference details.
    """
    __tablename__ = 'tickets'
    
    # Primary identification
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    message_id = db.Column(db.String(32), db.ForeignKey('messages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    
    # Ticket content and metadata
    accident_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(32), nullable=False)
    industry_type = db.Column(db.String(32), nullable=False)
    title = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # hex color code
    
    def __repr__(self):
        return f'<Ticket {self.ticket_id}>'
    
    def to_dict(self):
        """Convert ticket to dictionary format for API responses."""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'created_at': self.created_at,
            'accident_id': self.accident_id,
            'event_type': self.event_type,
            'industry_type': self.industry_type,
            'title': self.title,
            'url': self.url,
            'color': self.color
        }

    def save(self):
        """Save ticket to database."""
        db.session.add(self)
        db.session.commit()

class Message(db.Model):
    """
    Model representing chat messages.
    
    Messages can be from users or the model (system) and can have associated tickets.
    """
    # Constants for message source
    SOURCE_MODEL = False  # Message from the system/model
    SOURCE_USER = True   # Message from a user
    
    # Constants for message processing status
    STATUS_ERROR = -1    # Processing failed
    STATUS_PENDING = 0   # Not yet processed
    STATUS_SUCCESS = 1   # Successfully processed
    
    __tablename__ = 'messages'
    
    # Primary fields
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chats.id'), nullable=False)
    source = db.Column(db.Boolean, default=False)  # True for user, False for model
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    
    # Relationships and status
    tickets = db.relationship('Ticket', backref='message', lazy=True, cascade="all, delete-orphan")
    status = db.Column(db.Integer, default=0, nullable=False)
    
    def list_tickets(self) -> List[Ticket]:
        """Get all tickets associated with this message."""
        return Ticket.query.filter_by(message_id=self.id).all()
        
    def __repr__(self):
        return f'<Message {self.message}>'
    
    def to_dict(self):
        """Convert message to dictionary format for API responses."""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'source': self.source,
            'message': self.message,
            'status': self.status,
            'tickets': [ticket.to_dict() for ticket in self.list_tickets()],
            'created_at': self.created_at
        }
    
    def save(self):
        """Save message to database."""
        db.session.add(self)
        db.session.commit()

class Chat(db.Model):
    """
    Model representing a chat conversation.
    
    Contains messages between a user and the system, with support for
    naming, updating, and managing message history.
    """
    __tablename__ = 'chats'
    
    # Primary fields
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.Text, nullable=False, default='New Chat')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<Chat {self.message}>'
    
    @staticmethod
    def create(user_id: str, name: str) -> 'Chat | None':
        """Create a new chat with given user_id and name."""
        if not user_id:
            return None
        if not name:
            name = 'New Chat'
        chat = Chat(user_id=user_id, name=name)
        db.session.add(chat)
        db.session.commit()
        return chat

    def delete(self) -> bool:
        """Delete chat and all associated messages."""
        messages = Message.query.filter_by(chat_id=self.id).all()
        for message in messages:
            db.session.delete(message)
        db.session.delete(self)
        db.session.commit()
        return True

    @staticmethod
    def list(user_id: str) -> List['Chat']:
        """Get all chats for a given user."""
        return Chat.query.filter_by(user_id=user_id).all() if user_id else []

    @staticmethod
    def get(user_id: str, chat_id: str) -> 'Chat | None':
        """Get specific chat by user_id and chat_id."""
        return Chat.query.filter_by(user_id=user_id, id=chat_id).first() if user_id and chat_id else None

    def rename(self, name) -> bool:
        """Rename the chat."""
        if not name:
            return False
        self.name = name
        self.updated_at = datetime.datetime.now()
        db.session.commit()
        return True
    
    def messages(self) -> List[Message]:
        """Get all messages in the chat."""
        return Message.query.filter_by(user_id=self.user_id, chat_id=self.id).all()
    
    def add_message(self, msg: Message | dict) -> bool:
        """
        Add a new message to the chat.
        Accepts either Message object or dictionary of message data.
        """
        if isinstance(msg, dict):
            msg = Message(**msg)
            
        if msg.chat_id != self.id:
            return False
        msg.chat_id = self.id
        msg.user_id = self.user_id
        db.session.add(msg)
        db.session.commit()
        return True
    
    def remove_message(self, msg: Message | str) -> bool:
        """
        Remove a message from the chat.
        Accepts either Message object or message ID.
        """
        if isinstance(msg, str):
            msg = Message.query.get(msg)
        if msg.chat_id != self.id:
            return False
        
        db.session.delete(msg)
        db.session.commit()
        return True
    
    def history(self):
        """
        Get chat history formatted for model context.
        Returns list of message dictionaries with role and content.
        """
        return [
            {'role': 'user' if message.source else 'model', 'parts': message.message}
            for message in self.messages()
        ]
        
    def last_updated(self):
        """Get timestamp of most recent message or chat update."""
        msgs = self.messages()
        last_updated = self.updated_at
        for msg in msgs:
            if msg.created_at > last_updated:
                last_updated = msg.created_at
        return last_updated

    def to_dict(self):
        """Convert chat to dictionary format for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': int(self.created_at.timestamp() * 1000),
            'modified_at': int(self.last_updated().timestamp() * 1000),
        }