from app.models.models import Complaint


class ComplaintBuild:
    def __init__(self, query):
        self.query = query

    def filter_category(self, category):
        if category is not None:
            self.query = self.query.filter(Complaint.category == category)
        return self

    def filter_status(self, status):
        if status is not None:
            self.query = self.query.filter(Complaint.status == status)
        return self

    def filter_by_pagination(self, page, limit):
        if page is not None and limit is not None:
            self.query = self.query.offset((page - 1) * limit).limit(limit)
        return self

    def build(self):
        return self.query
