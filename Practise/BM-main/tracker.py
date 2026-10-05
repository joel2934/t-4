"""
Action-item tracker utilities.
Stores a small status file that maps action IDs to status (open/done) and supports listing.
"""
import os
import json
import uuid
from typing import Dict, Any, List

TRACKER_PATH = os.path.join(os.path.dirname(__file__), 'data', 'action_tracker.json')


def _ensure_tracker():
    d = os.path.dirname(TRACKER_PATH)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(TRACKER_PATH):
        with open(TRACKER_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f)


def _read_tracker() -> Dict[str, Any]:
    _ensure_tracker()
    with open(TRACKER_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_tracker(data: Dict[str, Any]):
    _ensure_tracker()
    with open(TRACKER_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def capture_actions(transcript_id: str, actions: List[Dict[str, Any]]) -> List[str]:
    """Add actions to tracker, return list of action ids created."""
    data = _read_tracker()
    ids = []
    for a in actions:
        aid = str(uuid.uuid4())
        rec = {
            'id': aid,
            'transcript_id': transcript_id,
            'task': a.get('task'),
            'owner': a.get('owner'),
            'deadline': a.get('deadline'),
            'status': 'open'
        }
        data[aid] = rec
        ids.append(aid)
    _write_tracker(data)
    return ids


def list_actions(status: str = None, transcript_id: str = None) -> List[Dict[str, Any]]:
    data = _read_tracker()
    res = list(data.values())
    if status:
        res = [r for r in res if r.get('status') == status]
    if transcript_id:
        res = [r for r in res if r.get('transcript_id') == transcript_id]
    return res


def set_action_status(action_id: str, status: str) -> bool:
    data = _read_tracker()
    if action_id not in data:
        return False
    data[action_id]['status'] = status
    _write_tracker(data)
    return True


def get_action(action_id: str) -> Dict[str, Any]:
    data = _read_tracker()
    return data.get(action_id)
