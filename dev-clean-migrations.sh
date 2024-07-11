#!/bin/bash
# Delete migrations
sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
sudo find . -path "*/migrations/*.pyc"  -delete