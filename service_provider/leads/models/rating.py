from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from leads.models.job import Job
from authorization.models.user import User


class Rating(BaseModel):
    reliability = models.IntegerField(
        null=False, validators=[
            MinValueValidator(0), MaxValueValidator(5)])
    courtesy = models.IntegerField(
        null=False,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)])
    professionalism = models.IntegerField(
        null=False, validators=[
            MinValueValidator(0), MaxValueValidator(5)])
    job_performance = models.IntegerField(
        null=False, validators=[
            MinValueValidator(0), MaxValueValidator(5)])

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,related_name='rating_user')
    review = models.CharField(max_length=500, blank=True, null=True)
    response = models.CharField(max_length=500, blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE,related_name="rating_job")
