from typing import Optional, Tuple, Union
from django.db import models
from django.db.models import CheckConstraint, Q, F, Max
from django.shortcuts import get_object_or_404


class MenuManager(models.Manager):
    def get_tree(self, root: Union[int, str]):
        """retrives tree with root and all descendants
        Args:
            root (Union[int, str]): id or name of root node
        """
        if type(root) == int:
            q = Q(id=root)
        elif type(root) == str:
            q = Q(name=root)
        else:
            raise TypeError(
                "root argument should be either int for id or str for name lookup"
            )

        root = get_object_or_404(MenuItem, q)
        return self.filter(lft__range=(root.lft, root.rgt)).order_by("lft")

    def get_descendants(self, id: int, direct_only: bool = False):
        top = get_object_or_404(MenuItem, id=id)
        if direct_only:
            return self.filter(
                lft__range=(top.lft + 1, top.rgt - 1), parent=top
            ).order_by("lft")
        else:
            return self.filter(lft__range=(top.lft + 1, top.rgt - 1)).order_by("lft")


class MenuItem(models.Model):
    """Implementation of menu item node based on nested set model.
    Do not change lft and rgt values directly unless you know what you are doing"""

    _position_updater = None
    name = models.CharField(max_length=100)
    lft = models.PositiveIntegerField(null=False)
    rgt = models.PositiveIntegerField(null=False)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    objects = MenuManager()

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(lft__gt=0),
                name="check_left",
            ),
            CheckConstraint(
                check=Q(rgt__gt=1),
                name="check_right",
            ),
            CheckConstraint(
                check=Q(lft__lt=F("rgt")),
                name="node_okay",
            ),
        ]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.id:  # create
            if self.parent:  # new node
                self._create_new_child_node()
            else:  # new root
                boundary = MenuItem.objects.aggregate(Max("rgt"))["rgt__max"] or 0
                self.lft = boundary + 1
                self.rgt = boundary + 2
        else:  # update
            old_obj = MenuItem.objects.get(id=self.id)
            old_pos = old_obj.get_position()
            # move node under new parent if changed
            if (
                self.parent_id != old_obj.parent_id
                or old_pos
                and self._position_updater
                and old_pos[0] != self._position_updater
            ):
                self._update_node_position()

        self._position_updater = None
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        width = self.rgt - self.lft + 1
        MenuItem.objects.filter(lft__range=(self.lft, self.rgt)).delete()
        MenuItem.objects.filter(lft__gt=self.rgt).update(lft=F("lft") - width)
        MenuItem.objects.filter(rgt__gt=self.rgt).update(rgt=F("rgt") - width)

        return super().delete(*args, **kwargs)

    def get_position(self) -> Optional[Tuple[int, int]]:
        """returns position of this node among siblings and total siblings count, or none if root node"""
        if self.parent:
            siblings = list(
                MenuItem.objects.get_descendants(self.parent_id, True).values_list(
                    "id", flat=True
                )
            )
            position = siblings.index(self.id) + 1
            total = len(siblings)

            return position, total

    def set_new_position(self, position: int):
        if position < -1:
            raise ValueError("position should not be less than -1")
        self._position_updater = position

    def _create_new_child_node(self):
        descendants = MenuItem.objects.get_descendants(self.parent_id, direct_only=True)

        if (
            self._position_updater == None
            or self._position_updater == -1
            or self._position_updater > len(descendants)
        ):
            self._position_updater = len(descendants)

        # no children or insert as first child
        if self._position_updater == 0 or not descendants:
            boundary = self.parent.lft
        else:
            boundary = descendants[self._position_updater - 1].rgt

        MenuItem.objects.filter(rgt__gt=boundary).update(rgt=F("rgt") + 2)
        MenuItem.objects.filter(lft__gt=boundary).update(lft=F("lft") + 2)

        self.lft = boundary + 1
        self.rgt = boundary + 2

    def _update_node_position(self):
        tree_ids = list(MenuItem.objects.get_tree(self.id).values_list("id", flat=True))

        # update previous obj place
        offset = self.rgt - self.lft + 1
        source_boundary = self.lft

        MenuItem.objects.filter(lft__gt=source_boundary).exclude(
            id__in=tree_ids
        ).update(lft=F("lft") - offset)

        MenuItem.objects.filter(rgt__gt=source_boundary).exclude(
            id__in=tree_ids
        ).update(rgt=F("rgt") - offset)

        # update new obj place

        target_descendants = MenuItem.objects.get_descendants(
            self.parent_id, direct_only=True
        )

        if (
            self._position_updater == None
            or self._position_updater == -1
            or self._position_updater > len(target_descendants)
        ):
            self._position_updater = len(target_descendants)

        # target has no children or insert as first child
        if self._position_updater == 0 or not target_descendants:
            target_boundary = self.parent.lft
        else:
            target_boundary = target_descendants[self._position_updater - 1].rgt

        MenuItem.objects.filter(rgt__gt=target_boundary).exclude(
            id__in=tree_ids
        ).update(rgt=F("rgt") + offset)

        MenuItem.objects.filter(lft__gt=target_boundary).exclude(
            id__in=tree_ids
        ).update(lft=F("lft") + offset)

        # update inserted tree
        shift = target_boundary - source_boundary + 1

        MenuItem.objects.filter(id__in=tree_ids).update(
            lft=F("lft") + shift, rgt=F("rgt") + shift
        )

        self.lft += shift
        self.rgt += shift
