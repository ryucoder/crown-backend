import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration


ENVIRONMENT = "local"

if ENVIRONMENT == "staging":
    from crown_backend.crown_settings.staging import *

else:
    from crown_backend.crown_settings.local import *

print()
print("ENVIRONMENT")
print(ENVIRONMENT)
print()
print()
print("DOMAIN_NAME")
print(DOMAIN_NAME)
print()
print()


sentry_sdk.init(
    dsn="https://f14bd43a38d649eb9905aaaf441a07b1@o484748.ingest.sentry.io/5622732",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    environment=ENVIRONMENT,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
