from pydantic import BaseModel


class DropOffs(BaseModel):
    visit_to_signup: float
    signup_to_first_action: float
    visit_to_pricing: float


class FunnelStats(BaseModel):
    total_leads: int
    signed_up: int
    first_actions: int
    pricing_views: int
    signup_conversion_rate: float
    drop_offs: DropOffs


class LostOpportunities(BaseModel):
    total_leads: int
    actual_signups: int
    expected_signups_at_baseline: int
    lost_signups: int
    baseline_used: float


class LeadsSummary(BaseModel):
    total_leads: int
    anonymous_leads: int
    signed_up_leads: int
    enriched_leads: int
    leads_with_pricing_view: int
    pending_enrichment: int


class TimeSeriesPoint(BaseModel):
    date: str
    new_leads: int
    signups: int
    pricing_views: int
    first_actions: int


class OverTimeStats(BaseModel):
    granularity: str
    from_date: str
    to_date: str
    series: list[TimeSeriesPoint]


class ConfidenceBreakdown(BaseModel):
    High: int
    Medium: int
    Low: int


class EnrichmentStats(BaseModel):
    total_enriched: int
    not_enriched: int
    confidence_breakdown: ConfidenceBreakdown

