import json
import logging
import re

from services.ollama_client import generate_answer

logger = logging.getLogger(__name__)


def _fallback_assessment(centre, status, bottlenecks):
    processing_rate = status.get('processingRate', 0)
    farmers_waiting = status.get('farmersWaiting', 0)
    storage_capacity = status.get('storageCapacity', 0)
    storage_used = status.get('storageUsed', 0)
    lifting_rate = status.get('liftingRate', 0)
    queue_hours = farmers_waiting / processing_rate if processing_rate else None
    storage_utilization = storage_used / storage_capacity if storage_capacity else None
    lifting_gap = max(processing_rate - lifting_rate, 0)

    score = 0
    if queue_hours is not None:
        score += min(queue_hours / 6, 1) * 45
    if storage_utilization is not None:
        score += min(storage_utilization, 1) * 35
    if processing_rate:
        score += min(lifting_gap / processing_rate, 1) * 20
    score = round(min(score, 100), 1)
    return {
        'riskScore': score,
        'riskLevel': 'high' if score >= 70 else 'medium' if score >= 35 else 'low',
        'confidence': 'low',
        'forecast': 'Deterministic fallback; LLM assessment unavailable.',
        'riskFactors': [item['type'] for item in bottlenecks],
        'recommendedActions': [],
        'queueHours': round(queue_hours, 2) if queue_hours is not None else None,
        'storageUtilization': round(storage_utilization * 100, 1)
        if storage_utilization is not None else None,
        'liftingGap': lifting_gap,
        'assessmentSource': 'deterministic_fallback',
        'dataSource': 'current_database_status',
    }


def _parse_json(response):
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:
        raise ValueError('LLM returned no JSON object')
    result = json.loads(match.group(0))
    score = float(result['riskScore'])
    if not 0 <= score <= 100:
        raise ValueError('LLM risk score is outside 0-100')
    result['riskScore'] = round(score, 1)
    result['riskLevel'] = (
        'high' if score >= 70 else 'medium' if score >= 35 else 'low'
    )
    result['confidence'] = result.get('confidence', 'low')
    result['riskFactors'] = result.get('riskFactors', [])
    result['recommendedActions'] = result.get('recommendedActions', [])
    result['assessmentSource'] = 'llm'
    result['dataSource'] = 'current_database_status'
    return result


def assess_risk_with_llm(
    centre,
    status,
    available_slots,
    request_counts,
    bottlenecks,
    recent_history=None,
):
    fallback = _fallback_assessment(centre, status, bottlenecks)
    data = {
        'centre': centre,
        'currentStatus': status,
        'availableSlots': available_slots,
        'slotRequestCounts': request_counts,
        'detectedBottlenecks': bottlenecks,
        'recentRiskHistory': recent_history or [],
    }
    prompt = (
        'You are a procurement operations risk assessor. Assess the centre using only the '
        'provided current database snapshot. Consider every factor: farmers waiting, queue age, processing and '
        'lifting capacity, storage utilization, available slot supply, incoming request '
        'pressure, centre status, detected bottlenecks, and possible near-future scenarios. '
        'Estimate how the situation may change if arrivals continue and capacity does not '
        'change. Do not invent facts. Return ONLY valid JSON with exactly these useful keys: '
        'riskScore (number 0-100), confidence (high/medium/low), forecast (short string), '
        'riskFactors (array of strings), recommendedActions (array of strings), '
        'queueHours (number or null), storageUtilization (number or null), '
        'liftingGap (number).\n\n'
        f'Centre assessment data:\n{json.dumps(data, default=str, indent=2)}'
    )
    try:
        assessment = _parse_json(generate_answer(prompt))
        assessment.setdefault('queueHours', fallback['queueHours'])
        assessment.setdefault('storageUtilization', fallback['storageUtilization'])
        assessment.setdefault('liftingGap', fallback['liftingGap'])
        return assessment
    except Exception:
        logger.exception('LLM risk assessment failed for centre %s', centre.get('name'))
        return fallback