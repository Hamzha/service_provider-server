from authorization.models.base import BaseModel
from django.db import models
from django.core.validators import MinValueValidator


class Configuration(BaseModel):
    lead_charge = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Lead charges")
    urgent_service_charges = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Urgent service charges")
    regular_service_charges = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Regular service charges")
    job_cancellation_charges = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Job cancellation charges")
    otp_expiry = models.IntegerField(
        blank=False, null=False, validators=[
            MinValueValidator(1)], verbose_name="Otp Expiry")
    vendor_per_search = models.IntegerField(
        blank=False, null=False, validators=[
            MinValueValidator(1)], verbose_name="Vendor per search")

    first_late_penality_charge = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="First late penality charge")
    first_late_penality_timestamp = models.IntegerField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="First late penality timestamp")

    second_late_penality_charge = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Second late penality charge")
    second_late_penality_timestamp = models.IntegerField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Second late penality timestamp")

    third_late_penality_charge = models.FloatField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Third late penality charge")
    third_late_penality_timestamp = models.IntegerField(
        blank=False, null=False, validators=[
            MinValueValidator(0)], verbose_name="Third late penality timestamp")
