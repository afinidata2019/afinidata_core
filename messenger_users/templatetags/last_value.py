from django import template

register = template.Library()


def get_last_value(user, args):
    data = user.userdata_set.filter(data_key=args).order_by('-created')
    if not data.count() > 0:
        return None
    return data.first().data_value


register.filter('get_last_value', get_last_value)

