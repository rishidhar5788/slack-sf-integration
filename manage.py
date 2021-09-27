#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
# app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    main()
