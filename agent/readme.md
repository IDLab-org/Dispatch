```
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install aries-cloudagent \
            aries-askar \
            indy-vdr \
            indy-credx
aca-py start --arg-file ./config.yaml

```

```docker run ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.9.0 -v ```