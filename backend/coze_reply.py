"""
Coze AI auto-reply integration
Calls the Coze workflow API to generate automatic replies for buyer inquiries.
"""
import json
import requests
import threading
from models import db, Message, User, Inquiry

COZE_URL = "https://g7p55np2tg.coze.site/run"
COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImFlNGZkZTBhLWUzZWItNGRkYi1iYWEzLTg0MzY3MzcyZmQ2ZSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbInVmZ1cyMVBGZzZEMVRoUGVUeGZXWWMyZWdkcEZiM2JKIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc0NDk0OTUyLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjIxMzg5NDA5ODc4ODAyNDcwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjIxMzk3Nzg2MDQyMzAyNDc5In0.LioAIG3Js6AiBQRTKKSmE84n5GcNlCIMYesH816XiYqb9May-7KXqPi4t9xKaeWSiT9Bp6TL5hhPlzgGzTo50AJ0tuUPWIH6jiVlcGtsjKlh73CiXgZYkFMzT7W9dvCRVFzMS3LEhbrxOvmyv2kGLGjqe_uxoMHebdxKtRm4HClILd8ivRrlYbOcsfkNwqltMB8zIBwOFPV6b1l3KF7NXX_jAyd5DD0zdRGQ6pmycCMf8fQ3L-9NUR4qgjAEw_KNzf0GcKT70gkmXeie06bnnwX3FqDLX5VGps-68drl3xXUlPC_5yqE-SlSAp74Of9iTd-4RhbvgZw0G1Rj8H8REQ"


def get_auto_reply(user_question):
    """Call Coze API and return the clean reply text."""
    try:
        resp = requests.post(
            COZE_URL,
            headers={
                "Authorization": f"Bearer {COZE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"user_question": user_question},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                # Extract final_answer from Coze response
                answer = data.get('final_answer') or data.get('output') or data.get('answer') or data.get('reply')
                if answer:
                    return answer.strip()
                # Try nested data
                inner = data.get('data')
                if isinstance(inner, dict):
                    answer = inner.get('final_answer') or inner.get('output')
                    if answer:
                        return answer.strip()
            return None
    except Exception as e:
        print(f"[Coze] Auto-reply error: {e}")
    return None


def build_inquiry_context(inq):
    """Build a meaningful question from inquiry data for Coze."""
    parts = []
    if inq.product:
        parts.append(f"Product: {inq.product.title}")
        if inq.product.title_en:
            parts.append(f"({inq.product.title_en})")
    if inq.quantity:
        parts.append(f"Quantity: {inq.quantity}")
    if inq.message:
        # For wishlist JSON messages, extract the text part
        msg_text = inq.message
        try:
            parsed = json.loads(inq.message)
            if isinstance(parsed, dict) and 'text' in parsed:
                msg_text = parsed.get('text', '')
        except (json.JSONDecodeError, TypeError):
            pass
        if msg_text:
            parts.append(f"Message: {msg_text}")
    if not parts:
        return None
    return "Customer inquiry - " + " | ".join(parts)


def trigger_auto_reply(app, inquiry_id, user_question):
    """Run in a background thread: call Coze, insert reply as admin message."""
    def _do():
        with app.app_context():
            try:
                reply = get_auto_reply(user_question)
                if not reply or not reply.strip():
                    return

                admin = User.query.filter_by(role='admin').first()
                if not admin:
                    return

                inq = Inquiry.query.get(inquiry_id)
                if not inq or inq.status in ('closed', 'quoted'):
                    return

                msg = Message(
                    inquiry_id=inquiry_id,
                    sender_id=admin.id,
                    content=reply.strip(),
                    msg_type='text',
                )
                db.session.add(msg)

                if inq.status == 'new':
                    inq.status = 'contacted'

                db.session.commit()
                print(f"[Coze] Auto-replied to inquiry #{inquiry_id}")
            except Exception as e:
                print(f"[Coze] Failed to save auto-reply: {e}")
                db.session.rollback()

    threading.Thread(target=_do, daemon=True).start()


def trigger_inquiry_auto_reply(app, inquiry_id, lang='zh'):
    """Auto-reply for new inquiry submissions — fixed confirmation message, no AI."""
    def _do():
        with app.app_context():
            try:
                inq = Inquiry.query.get(inquiry_id)
                if not inq or inq.status in ('closed', 'quoted'):
                    return

                admin = User.query.filter_by(role='admin').first()
                if not admin:
                    return

                product_name = ''
                if inq.product:
                    if lang == 'zh':
                        product_name = inq.product.title or inq.product.title_en or ''
                    else:
                        product_name = inq.product.title_en or inq.product.title or ''

                if lang == 'zh':
                    if product_name:
                        reply = f"感谢您对 [{product_name}] 的询盘，我们已收到您的需求，团队将尽快为您核实价格和库存信息，预计24小时内回复。"
                    else:
                        reply = "感谢您的询盘，我们已收到您的需求，团队将在24小时内回复您。"
                else:
                    if product_name:
                        reply = f"Thank you for your inquiry about [{product_name}]. We have received your request and our team will get back to you with pricing and availability within 24 hours."
                    else:
                        reply = "Thank you for your inquiry. We have received your request and our team will get back to you within 24 hours."

                msg = Message(
                    inquiry_id=inquiry_id,
                    sender_id=admin.id,
                    content=reply,
                    msg_type='text',
                )
                db.session.add(msg)

                if inq.status == 'new':
                    inq.status = 'contacted'

                db.session.commit()
            except Exception as e:
                print(f"[AutoReply] Failed: {e}")
                db.session.rollback()

    threading.Thread(target=_do, daemon=True).start()
