"""
Report model — stores generated analysis reports for users.
"""
import json
from datetime import datetime
from backend.extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_role = db.Column(db.String(120), nullable=False)
    report_data = db.Column(db.Text, nullable=False)  # JSON blob
    ats_score = db.Column(db.Integer, default=0)
    hiring_readiness = db.Column(db.Integer, default=0)
    dsa_level = db.Column(db.String(20), default="N/A")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("reports", lazy="dynamic", order_by="Report.created_at.desc()"))

    def set_data(self, data: dict):
        self.report_data = json.dumps(data)

    def get_data(self) -> dict:
        try:
            return json.loads(self.report_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def to_dict(self):
        return {
            "id": self.id,
            "target_role": self.target_role,
            "ats_score": self.ats_score,
            "hiring_readiness": self.hiring_readiness,
            "dsa_level": self.dsa_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Report {self.id} for user {self.user_id}: {self.target_role}>"
