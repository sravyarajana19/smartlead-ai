from datetime import datetime, date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr


class PaginationMeta(BaseModel):
    total_records: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel):
    items: List[Any]
    meta: PaginationMeta


# Company Schemas
class CompanyBase(BaseModel):
    name: str
    domain: str
    industry: str
    employee_count: int
    annual_revenue: float
    country: str
    territory: str
    tier: str


class CompanyCreate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# Contact Schemas
class ContactBase(BaseModel):
    company_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    normalized_phone: Optional[str] = None
    job_title: str
    seniority_level: str
    department: str
    is_primary: bool = False


class ContactCreate(ContactBase):
    pass


class ContactOut(ContactBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# Campaign Schemas
class CampaignBase(BaseModel):
    name: str
    campaign_type: str
    channel: str
    budget: float
    start_date: date
    end_date: date
    target_territory: str
    target_product: str
    status: str = "Active"


class CampaignCreate(CampaignBase):
    pass


class CampaignOut(CampaignBase):
    id: str
    created_at: datetime
    model_config = {"from_attributes": True}


# SalesRep Schemas
class SalesRepBase(BaseModel):
    name: str
    email: str
    territory: str
    product_specialization: str
    is_active: bool = True
    capacity: int = 50
    current_load: int = 0


class SalesRepCreate(SalesRepBase):
    pass


class SalesRepOut(SalesRepBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# Lead Schemas
class LeadBase(BaseModel):
    company_id: str
    contact_id: str
    campaign_id: Optional[str] = None
    assigned_rep_id: Optional[str] = None
    lead_source: str
    product_interest: str
    territory: str
    status: str = "New"


class LeadCreate(LeadBase):
    pass


class LeadOut(LeadBase):
    id: str
    fit_score: float
    intent_score: float
    engagement_score: float
    lead_score: float
    priority: str
    is_duplicate: bool
    canonical_lead_id: Optional[str] = None
    is_converted: bool
    converted_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# Activity Schemas
class ActivityBase(BaseModel):
    lead_id: str
    activity_type: str
    channel: str
    intent_weight: float = 0.0
    engagement_weight: float = 0.0
    activity_date: datetime
    metadata_json: Optional[str] = None
    is_post_conversion: bool = False


class ActivityCreate(ActivityBase):
    pass


class ActivityOut(ActivityBase):
    id: str
    created_at: datetime
    model_config = {"from_attributes": True}


# Consent Schemas
class ConsentBase(BaseModel):
    lead_id: str
    contact_id: str
    consent_status: str
    consent_type: str = "All"
    channel: str
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    opt_out_timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class ConsentCreate(ConsentBase):
    pass


class ConsentOut(ConsentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# Task Schemas
class TaskBase(BaseModel):
    lead_id: str
    assigned_rep_id: str
    task_type: str
    priority: str = "Normal"
    due_date: datetime
    status: str = "Pending"
    blocked_reason: Optional[str] = None
    is_consent_verified: bool = False


class TaskCreate(BaseModel):
    lead_id: str
    task_type: str
    priority: Optional[str] = "Normal"
    due_date: Optional[datetime] = None
    assigned_rep_id: Optional[str] = None


class TaskOut(TaskBase):
    id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# Opportunity Schemas
class OpportunityBase(BaseModel):
    lead_id: str
    company_id: str
    assigned_rep_id: str
    opportunity_value: float
    currency: str = "USD"
    current_stage: str = "New"
    creation_date: datetime
    expected_close_date: datetime
    actual_close_date: Optional[datetime] = None
    won_lost_reason: Optional[str] = None
    is_duplicate: bool = False
    canonical_opp_id: Optional[str] = None


class OpportunityCreate(BaseModel):
    lead_id: str
    opportunity_value: float
    expected_close_date: datetime
    currency: Optional[str] = "USD"


class StageTransitionRequest(BaseModel):
    new_stage: str
    changed_by: Optional[str] = "Sales Agent"
    won_lost_reason: Optional[str] = None
    notes: Optional[str] = None


class OpportunityOut(OpportunityBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# StageHistory Schemas
class StageHistoryOut(BaseModel):
    id: str
    opportunity_id: str
    from_stage: Optional[str]
    to_stage: str
    stage_duration_days: int
    transition_date: datetime
    changed_by: str
    is_valid_transition: bool
    notes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# Scoring Schemas
class ScoreExplanation(BaseModel):
    lead_id: str
    fit_score: float
    intent_score: float
    engagement_score: float
    lead_score: float
    priority: str
    rule_version: str
    fit_weight: float
    intent_weight: float
    engagement_weight: float
    explanation_details: Dict[str, Any]
    is_leakage_detected: bool = False


# Routing Schemas
class RoutingRequest(BaseModel):
    lead_id: str


class RoutingResponse(BaseModel):
    lead_id: str
    assigned_rep_id: Optional[str]
    rep_name: Optional[str]
    territory: str
    product_interest: str
    routing_status: str  # Assigned, Fallback, MismatchDetected, NoCapacity
    message: str


# Validation Schemas
class ValidationSummaryResponse(BaseModel):
    total_records_checked: int
    passed_checks: int
    failed_checks: int
    warnings: int
    detected_anomalies: int
    validation_status: str
    case_breakdown: Dict[str, int]
    details: List[Dict[str, Any]]


# ML Schemas
class MLEvaluationMetrics(BaseModel):
    model_type: str
    train_size: int
    test_size: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float]
    confusion_matrix: List[List[int]]
    feature_importance: Dict[str, float]
    evaluated_at: datetime


class MLPredictionRequest(BaseModel):
    lead_id: str


class MLPredictionResponse(BaseModel):
    lead_id: str
    rule_score: float
    priority: str
    conversion_probability: float
    predicted_conversion: bool
    explanation: Dict[str, Any]


# Dashboard Metrics Schema
class DashboardMetricsResponse(BaseModel):
    total_leads: int
    high_priority_leads: int
    qualified_leads: int
    total_opportunities: int
    won_opportunities: int
    conversion_rate: float
    won_revenue: float
    pipeline_value: float
    lead_priority_distribution: Dict[str, int]
    funnel_stages: Dict[str, int]
    territory_breakdown: Dict[str, int]
    monthly_trends: List[Dict[str, Any]]
