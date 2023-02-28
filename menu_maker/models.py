from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.shortcuts import get_object_or_404


class MenuManager(models.Manager):
    def get_descendants(self, id: int, direct_only: bool = False):
        top = get_object_or_404(MenuItem, id=id)
        if direct_only:
            return self.filter(
                lft__range=(top.lft + 1, top.rgt - 1), parent=top
            ).order_by("lft")
        else:
            return self.filter(lft__range=(top.lft + 1, top.rgt - 1)).order_by("lft")


class MenuItem(models.Model):
    """Implementation of menu item node based on nested set model"""

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
