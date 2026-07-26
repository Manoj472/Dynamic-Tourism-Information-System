from django.db import models
from django.utils.text import slugify



class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="states"
    )

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("country", "name")

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    name = models.CharField(max_length=100)

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="cities/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("state", "name")

    def __str__(self):
        return self.name


class TouristAttraction(models.Model):

    CATEGORY_CHOICES = [
        ("Beach", "Beach"),
        ("Park", "Park"),
        ("Temple", "Temple"),
        ("Museum", "Museum"),
        ("Monument", "Monument"),
        ("Hill", "Hill"),
        ("Lake", "Lake"),
        ("Adventure", "Adventure"),
        ("Historical", "Historical"),
        ("Other", "Other"),
    ]

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="attractions"
    )

    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    source = models.CharField(
        max_length=100,
        default="OpenTripMap"
    )

    name = models.CharField(max_length=255)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Others"
    )

    description = models.TextField(
        blank=True
    )

    latitude = models.FloatField()

    longitude = models.FloatField()

    rating = models.FloatField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("city", "name")

    def __str__(self):
        return self.name


class AttractionImage(models.Model):

    attraction = models.ForeignKey(
        TouristAttraction,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image_url = models.URLField()

    is_primary = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attraction.name} Image"


class Accommodation(models.Model):

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="accommodations"
    )

    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    name = models.CharField(max_length=255)

    address = models.TextField()

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    rating = models.FloatField(
        null=True,
        blank=True
    )

    image_url = models.URLField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Activity(models.Model):

    CATEGORY_CHOICES = [
        ("outdoor-adventure", "Outdoor & Adventure"),
        ("mindfulness", "Mindfulness"),
        ("sports", "Sports"),
        ("entertainment", "Entertainment"),
        ("nature", "Nature"),
    ]

    city = models.ForeignKey(
        "City",
        on_delete=models.CASCADE,
        related_name="activities"
    )

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    image_url = models.URLField(
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class LocalFood(models.Model):

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="foods"
    )

    name = models.CharField(max_length=255)

    description = models.TextField()

    image_url = models.URLField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Culture(models.Model):

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="cultures"
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Transportation(models.Model):

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="transportations"
    )

    transport_type = models.CharField(max_length=100)

    details = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transport_type


class WeatherCache(models.Model):

    city = models.OneToOneField(
        City,
        on_delete=models.CASCADE,
        related_name="weather"
    )

    temperature = models.FloatField()

    condition = models.CharField(
        max_length=100
    )

    humidity = models.IntegerField()

    wind_speed = models.FloatField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.city.name} Weather"


class ContactInfo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    discord_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Contact Info"
        verbose_name_plural = "Contact Info"

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    newsletter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
