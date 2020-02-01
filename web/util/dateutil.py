import datetime
class DateUtil(object):
    @classmethod
    def convertDateToString(cls, date):
        print(type(date))
        value = ''
        try:
            value = date.strftime('%d/%m/%Y')
        except Exception as ex:
            print (ex)
            value = date
        return value

