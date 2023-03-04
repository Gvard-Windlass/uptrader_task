from typing import Any, Dict
from django import template
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.safestring import SafeString
from menu_maker.models import MenuItem
from dataclasses import dataclass


@dataclass
class Node:
    item: MenuItem
    is_parent = False
    hidden = True
    is_last_child = False
    is_active = False
    ul_iterator = None


register = template.Library()


def _tree_to_nodes(menu_items: QuerySet) -> Dict[int, Node]:
    menu_dict = {}
    for item in menu_items:
        menu_dict[item.id] = Node(item)
    return menu_dict


def _annotate_nodes(menu_dict: Dict[int, Node], active_id: int):
    if not menu_dict:
        return

    active_item = None
    nodes = list(menu_dict.values())
    for i, node in enumerate(nodes):
        if node.item.rgt - node.item.lft > 1:
            node.is_parent = True

        if node.item.parent_id:
            parent = menu_dict.get(node.item.parent_id).item or None
            if parent and node.item.rgt == parent.rgt - 1:
                node.is_last_child = True

        if node.item.id == active_id:
            node.is_active = True
            node.hidden = False
            active_item = node.item

        if node.is_last_child and not node.is_parent:
            if i < len(nodes) - 2:
                next_lft = nodes[i + 1].item.lft
                ul_n = next_lft - node.item.rgt - 1
            else:
                next_lft = nodes[0].item.rgt
                ul_n = next_lft - node.item.rgt

            node.ul_iterator = list(range(ul_n))

    if not active_item:
        return

    ancestor = menu_dict.get(active_item.parent_id) or None
    while ancestor:
        ancestor.hidden = False
        ancestor = menu_dict.get(ancestor.item.parent_id) or None


@register.inclusion_tag("menu_maker/menu.html", takes_context=True)
def draw_menu(context: Dict[str, Any], menu_name: SafeString):
    request: HttpRequest = context["request"]
    active_menu_item_id = request.resolver_match.kwargs.get("menu_item_id") or None
    menu_nodes = _tree_to_nodes(MenuItem.objects.get_tree(str(menu_name)))

    _annotate_nodes(menu_nodes, active_menu_item_id)
    nodes_list = sorted(list(menu_nodes.values()), key=lambda x: x.item.lft)

    return {
        "menu_nodes": nodes_list,
        "menu_name": menu_name,
    }
