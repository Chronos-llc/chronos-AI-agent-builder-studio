from typing import List

from pydantic import BaseModel

from app.schemas.integration import (
    IntegrationResponse,
    IntegrationSubmissionCreate,
    IntegrationSubmissionEventResponse,
    IntegrationSubmissionUpdate,
    IntegrationModerationRequest,
)


class IntegrationSubmissionListResponse(BaseModel):
    submissions: List[IntegrationResponse]
    total: int


class IntegrationSubmissionDetailResponse(BaseModel):
    submission: IntegrationResponse
    events: List[IntegrationSubmissionEventResponse]


class IntegrationSubmissionCreateRequest(IntegrationSubmissionCreate):
    pass


class IntegrationSubmissionUpdateRequest(IntegrationSubmissionUpdate):
    pass


class IntegrationModerationRequestBody(IntegrationModerationRequest):
    pass
