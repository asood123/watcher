### Watcher

This script waits downloads a specific website every minute and waits until registration is open. Then, fills out the form and submits it.

To try this out:

```bash
> cp myconfig_sample.py myconfig.py
```

Visit mailgun and sign up for free API. Plug in values that they give you into `myconfig.py`.

```
> pip install -r requirements.txt
> python watcher.py
```
