# lex_bot_export
# Programmatically Export Lex Bot into a CDK Project

1. Get temporary AWS IAM Credentials
```saml2aws login --force -p <PROFILE_NAME> --session-duration 35000```

2. Run Python Bot Export file
```python bot_export.py --version DRAFT --environment <YOUR_BOT_NAME>```
