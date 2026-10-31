import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(32), primary_key=True)  # CO-000001
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    employee_count = Column(Integer, nullable=False)
    annual_revenue = Column(Float, nullable=False)
    country = Column(String(100), nullable=False)
    territory = Column(String(50), nullable=False, index=True)
    tier = Column(String(50), nullable=False)  # Enterprise, Mid-Market, SMB
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(32), primary_key=True)  # CON-000001
    company_id = Column(String(32), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    normalized_phone = Column(String(50), nullable=True, index=True)
    job_title = Column(String(100), nullable=False)
    seniority_level = Column(String(50), nullable=False)  # C-Level, VP, Director, Manager, Individual
    department = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="contacts")
    leads = relationship("Lead", back_populates="contact")
    consents = relationship("Consent", back_populates="contact")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(32), primary_key=True)  # CMP-000001
    name = Column(String(255), nullable=False)
    campaign_type = Column(String(100), nullable=False)  # Webinar, Whitepaper, Product Launch, Email Blast, Search Ads, Partner Co-Marketing
    channel = Column(String(50), nullable=False)  # Email, Web, Social, Search, Event
    budget = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    target_territory = Column(String(50), nullable=False)
    target_product = Column(String(100), nullable=False)
    status = Column(String(50), default="Active", nullable=False)  # Active, Completed, Planned, Paused
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    leads = relationship("Lead", back_populates="campaign")


class SalesRep(Base):
    __tablename__ = "sales_reps"

    id = Column(String(32), primary_key=True)  # REP-000001
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    territory = Column(String(50), nullable=False, index=True)
    product_specialization = Column(String(100), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    capacity = Column(Integer, default=50, nullable=False)
    current_load = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    assigned_leads = relationship("Lead", back_populates="assigned_rep")
    assigned_tasks = relationship("Task", back_populates="assigned_rep")
    assigned_opportunities = relationship("Opportunity", back_populates="assigned_rep")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String(32), primary_key=True)  # LEAD-2026-000001
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False, index=True)
    contact_id = Column(String(32), ForeignKey("contacts.id"), nullable=False, index=True)
    campaign_id = Column(String(32), ForeignKey("campaigns.id"), nullable=True, index=True)
    assigned_rep_id = Column(String(32), ForeignKey("sales_reps.id"), nullable=True, index=True)
    canonical_lead_id = Column(String(32), ForeignKey("leads.id"), nullable=True, index=True)

    lead_source = Column(String(100), nullable=False, index=True)  # Website, Inbound Form, Referral, Event, Organic Search, Paid Campaign, Outbound
    product_interest = Column(String(100), nullable=False, index=True)
    territory = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="New", nullable=False, index=True)  # New, Contacted, Working, Qualified, Unqualified, Converted

    fit_score = Column(Float, default=0.0, nullable=False)
    intent_score = Column(Float, default=0.0, nullable=False)
    engagement_score = Column(Float, default=0.0, nullable=False)
    lead_score = Column(Float, default=0.0, nullable=False, index=True)
    priority = Column(String(20), default="Low", nullable=False, index=True)  # High, Medium, Low

    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)
    is_converted = Column(Boolean, default=False, nullable=False, index=True)
    converted_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="leads")
    contact = relationship("Contact", back_populates="leads")
    campaign = relationship("Campaign", back_populates="leads")
    assigned_rep = relationship("SalesRep", back_populates="assigned_leads")
    canonical_lead = relationship("Lead", remote_side=[id])

    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="lead", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="lead", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="lead")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(64), primary_key=True)  # ACT-LEAD-2026-000001-001
    lead_id = Column(String(32), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False, index=True)  # Page View, Pricing View, Whitepaper Download, Webinar Attend, Demo Request, Email Open, Email Click, Inbound Call
    channel = Column(String(50), nullable=False)  # Web, Email, Phone, Event
    intent_weight = Column(Float, default=0.0, nullable=False)
    engagement_weight = Column(Float, default=0.0, nullable=False)
    activity_date = Column(DateTime, nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)
    is_post_conversion = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    lead = relationship("Lead", back_populates="activities")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(String(32), primary_key=True)  # CNS-000001
    lead_id = Column(String(32), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(32), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_status = Column(String(50), default="Pending", nullable=False, index=True)  # Opt-In, Opt-Out, Pending
    consent_type = Column(String(50), default="All", nullable=False)  # Email, Phone, SMS, All
    channel = Column(String(50), nullable=False)  # Email, Phone, SMS, Web
    effective_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    opt_out_timestamp = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    lead = relationship("Lead", back_populates="consents")
    contact = relationship("Contact", back_populates="consents")


class ScoreRule(Base):
    __tablename__ = "score_rules"

    id = Column(String(32), primary_key=True)  # SCR-000001
    rule_version = Column(String(50), nullable=False, unique=True)
    fit_weight = Column(Float, default=0.40, nullable=False)
    intent_weight = Column(Float, default=0.35, nullable=False)
    engagement_weight = Column(Float, default=0.25, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    effective_start_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    effective_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True)  # TASK-LEAD-2026-000001-001
    lead_id = Column(String(32), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_rep_id = Column(String(32), ForeignKey("sales_reps.id"), nullable=False, index=True)
    task_type = Column(String(100), nullable=False)  # Discovery Call, Email Outreach, Product Demo, Contract Follow-up, Meeting
    priority = Column(String(20), default="Normal", nullable=False)  # Urgent, High, Normal, Low
    due_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), default="Pending", nullable=False, index=True)  # Pending, In Progress, Completed, Cancelled, Blocked
    blocked_reason = Column(Text, nullable=True)
    is_consent_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    lead = relationship("Lead", back_populates="tasks")
    assigned_rep = relationship("SalesRep", back_populates="assigned_tasks")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(32), primary_key=True)  # OPP-2026-000001
    lead_id = Column(String(32), ForeignKey("leads.id"), nullable=False, index=True)
    company_id = Column(String(32), ForeignKey("companies.id"), nullable=False, index=True)
    assigned_rep_id = Column(String(32), ForeignKey("sales_reps.id"), nullable=False, index=True)
    canonical_opp_id = Column(String(32), ForeignKey("opportunities.id"), nullable=True)

    opportunity_value = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    current_stage = Column(String(50), default="New", nullable=False, index=True)  # New, Qualified, Proposal, Negotiation, Won, Lost
    creation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    expected_close_date = Column(DateTime, nullable=False)
    actual_close_date = Column(DateTime, nullable=True)
    won_lost_reason = Column(String(255), nullable=True)
    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    lead = relationship("Lead", back_populates="opportunities")
    company = relationship("Company", back_populates="opportunities")
    assigned_rep = relationship("SalesRep", back_populates="assigned_opportunities")
    stage_history = relationship("StageHistory", back_populates="opportunity", cascade="all, delete-orphan")


class StageHistory(Base):
    __tablename__ = "stage_histories"

    id = Column(String(64), primary_key=True)  # STG-OPP-2026-000001-001
    opportunity_id = Column(String(32), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    from_stage = Column(String(50), nullable=True)
    to_stage = Column(String(50), nullable=False)
    stage_duration_days = Column(Integer, default=0, nullable=False)
    transition_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    changed_by = Column(String(100), default="System", nullable=False)
    is_valid_transition = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="stage_history")


class DuplicateRelationship(Base):
    __tablename__ = "duplicate_relationships"

    id = Column(String(32), primary_key=True)  # DUP-000001
    primary_lead_id = Column(String(32), ForeignKey("leads.id"), nullable=False, index=True)
    duplicate_lead_id = Column(String(32), ForeignKey("leads.id"), nullable=False, index=True)
    match_type = Column(String(50), nullable=False)  # Exact, Potential, Legitimate Repeat
    match_reason = Column(String(255), nullable=False)  # Same Email, Same Phone, Same Company & Domain
    similarity_score = Column(Float, default=1.0, nullable=False)
    status = Column(String(50), default="Detected", nullable=False)  # Detected, Merged, Dismissed
    detected_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class AnomalyRecord(Base):
    __tablename__ = "anomaly_records"

    id = Column(String(32), primary_key=True)  # ANM-000001
    entity_type = Column(String(50), nullable=False)  # Lead, Task, Activity, SalesRep, Opportunity, StageHistory
    entity_id = Column(String(64), nullable=False, index=True)
    issue_type = Column(String(100), nullable=False, index=True)  # CASE_1_CONSENT_VIOLATION, CASE_2_TEMPORAL_LEAKAGE, etc.
    severity = Column(String(20), default="High", nullable=False)  # Critical, High, Medium, Low
    ground_truth_label = Column(String(100), nullable=False)
    expected_decision = Column(String(255), nullable=False)
    actual_decision = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    detected_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolution_status = Column(String(50), default="Open", nullable=False)  # Open, Investigating, Resolved, Ignored


class ConsentHistory(Base):
    __tablename__ = "consent_histories"

    id = Column(String(32), primary_key=True)  # CNH-000001
    lead_id = Column(String(32), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=True)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
