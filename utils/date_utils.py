from datetime import date, timedelta

def get_week_dates(reference_date):
    monday = reference_date - timedelta(days=reference_date.weekday())
    return [monday + timedelta(days=i) for i in range(7)]
