from __future__ import annotations

from base64 import urlsafe_b64decode
from typing import Dict, Any, List, Tuple


def _decode_body_data(data: str | None) -> str:
    if not data:
        return ""
    # Gmail returns URL-safe base64 without padding sometimes
    padding = "=" * (-len(data) % 4)
    try:
        return urlsafe_b64decode(data + padding).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_body_and_attachments(payload: Dict[str, Any]) -> Tuple[str, str, List[Dict[str, Any]]]:
    """Traverse the MIME tree and return (text_body, html_body, attachments_metadata).

    - Collect text/plain into text_body and text/html into html_body.
    - For attachments (parts with body.attachmentId), return lightweight metadata
      so callers can fetch the content later if needed.
    """
    text_chunks: List[str] = []
    html_chunks: List[str] = []
    attachments: List[Dict[str, Any]] = []

    def traverse(part: Dict[str, Any]) -> None:
        mime_type = part.get("mimeType")
        body = part.get("body", {})
        data = body.get("data")
        attachment_id = body.get("attachmentId")

        if mime_type == "text/plain" and data:
            text_chunks.append(_decode_body_data(data))
        elif mime_type == "text/html" and data:
            html_chunks.append(_decode_body_data(data))
        elif attachment_id:
            attachments.append(
                {
                    "filename": part.get("filename"),
                    "mimeType": mime_type,
                    "attachmentId": attachment_id,
                    "size": body.get("size"),
                }
            )

        for child in part.get("parts", []) or []:
            traverse(child)

    traverse(payload)

    return "\n".join(text_chunks).strip(), "\n".join(html_chunks).strip(), attachments


def parse_message_full(msg: Dict[str, Any]) -> Dict[str, Any]:
    """Extract headers, text/html bodies, and attachment metadata from a Gmail message resource."""
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])
    header_map = {h.get("name", "").lower(): h.get("value", "") for h in headers}

    text_body, html_body, attachments = extract_body_and_attachments(payload)

    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "from": header_map.get("from", ""),
        "to": header_map.get("to", ""),
        "subject": header_map.get("subject", ""),
        "date": header_map.get("date", ""),
        "snippet": msg.get("snippet", ""),
        "text_body": text_body,
        "html_body": html_body,
        "attachments": attachments,
    }


