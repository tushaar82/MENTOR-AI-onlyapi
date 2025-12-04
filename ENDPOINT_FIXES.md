# Endpoint Test Failures - Analysis and Fixes

## Test Results Summary
- **Total Tests**: 44
- **Passed**: 24 (54%)
- **Failed**: 20 (46%)

## Critical Issues Identified

### 1. Vector Search Response Format Mismatch ❌

**Error**: `Field required [type=missing, input_value={'topic': 'Laws of Motion...', 'chunk_id']`

**Root Cause**: The `_gemini_based_search` function returns results with `chunk_id` field, but when converting to `SearchResult` model, the code doesn't include this field. The model validation is failing because the raw result dict still has `chunk_id` but the model doesn't expect it.

**Location**: `services/vector_search_service.py` line 866-880

**Fix Required**:
```python
# Current code (line 866-880):
result = SearchResultModel(
    topic=raw_result["topic_name"],
    chapter=raw_result["chapter_name"],
    content=raw_result["content"],
    similarity_score=raw_result["similarity_score"],
    rank=idx + 1,
    exam=raw_result["exam"],
    subject=raw_result["subject"],
    difficulty=raw_result["difficulty"],
    weightage=raw_result["weightage"],
    metadata=raw_result.get("metadata", {}) if include_metadata else {}
)

# The issue is that raw_result contains extra fields like chunk_id, topic_id, etc.
# that aren't being passed to the model but are expected by the response validator
```

**Solution**: The model is correct, but we need to ensure all required fields are properly mapped.

---

### 2. Study Center Learning Materials Endpoint ❌

**Error**: `"Failed to retrieve learning materials. Please try again later."`

**Endpoint**: `GET /api/study-center/materials/T01`

**Root Cause**: The learning materials service is likely failing to generate AI content or encountering an error in the Gemini API call.

**Location**: `routers/study_center_router.py` and `services/learning_material_service.py`

**Investigation Needed**: Check if:
- Gemini API key is valid
- Topic ID exists in the database
- Error handling is catching and masking the real error

---

### 3. RAG Question Generation Failure ❌

**Error**: `"Failed to generate questions: Generation failed: Failed to generate any valid questions for topic 'Kinematics'"`

**Endpoint**: `POST /api/rag/generate-questions`

**Ro