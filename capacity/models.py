from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User, Group
from simple_history.models import HistoricalRecords
from simple_history import register

# register the historical models
register(User)
register(Group)


class BackendPermissions(models.Model):
    url = models.CharField(max_length=100, blank=False, null=False)
    ip_addresses = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    get = models.BooleanField(default=False)
    post = models.BooleanField(default=False)
    put = models.BooleanField(default=False)
    patch = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True)
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class FrontendPermissions(models.Model):
    url = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    ip_addresses = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True)
    access = models.BooleanField(default=False)
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value