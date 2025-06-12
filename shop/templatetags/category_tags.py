from django import template

register = template.Library()

@register.inclusion_tag('shop/category_menu.html')
def draw_category_menu(categories, active_slug=None):
    return {'categories': categories, 'active_slug': active_slug} 