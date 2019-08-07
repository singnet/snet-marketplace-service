class FilterCondition:
    def __init__(self, filter_condition):
        self.attr = filter_condition["attr"]
        self.operator = filter_condition["operator"]
        self.value = filter_condition["value"]


class Filter:
    def __init__(self, filter):
        self.filter = filter["filter"]
        self.filter_conditions = []
        self.set_filter()

    def get_filter(self):
        return {"filter": self.filter_conditions}

    def set_filter(self):
        for rec in self.filter:
            self.filter_conditions.append(FilterCondition(rec["filter_condition"]))