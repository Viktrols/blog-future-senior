import datetime as dt


def year(request):
    current_year = dt.datetime.now().year
    return {'year': current_year}
