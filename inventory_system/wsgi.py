"""
WSGI config for inventory_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(default=os.getenv("postgresql://inventory_system_vvhi_user:ziFwCOpTqBWDMVLdNuS8o5dreS8vSLKJ@dpg-cv4nm93tq21c73fcqgq0-a/inventory_system_vvhi"))
}

