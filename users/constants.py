USER_TYPE_CHOICES = [
    ("admin", "admin"),
    ("owner", "owner"),
    ("employee", "employee"),
]

PASSWORD_CATEGORY_CHOICES = [
    ("signup", "signup"),
    ("reset", "reset"),
]


RESET_PASSWORD_TOKEN_EXPIRY_MINUTES = 15
MOBILE_TOKEN_EXPIRY_MINUTES = 15
SIGNUP_TOKEN_EXPIRY_MINUTES = 15

DEFAULT_DENTIST_PASSWORD = "123456789"

CUSTOM_ERROR_MESSAGES = {
    "CharField": {
        "blank": "server_blank",
        "invalid": "server_invalid",
        "max_length": "server_max_length",
        "min_length": "server_min_length",
        "null": "server_null",
        "required": "server_required",
    },
    "EmailField": {
        "blank": "server_blank",
        "invalid": "server_invalid",
        "max_length": "server_max_length",
        "min_length": "server_min_length",
        "null": "server_null",
        "required": "server_required",
    },
    "UUIDField": {
        "required": "server_required",
        "null": "server_null",
        "invalid": "server_invalid",
    },
}
