# Recharge page command

Use this reference after the APS CLI skill selects `recharge` for an APS Web recharge or top-up
page. This command obtains a link; it does not buy credits or complete payment. Use PICO AI
Generation Service credits as the user-facing credit name.

## Choose whether to open the browser

For a request for a link, URL, page, portal, or recharge entry point, do not open a browser:

```bash
pico-aps-cli-cn recharge --json
```

Only when the user explicitly asks to open or launch the page, add `--open`:

```bash
pico-aps-cli-cn recharge --open --json
```

There is no price or amount option; do not invent one or pass a requested recharge amount to the command. Do not invoke an operating-
system browser command yourself or rewrite the returned URL.

## Interpret the result

- Exit `0`: require `ok: true`, `command: "recharge"`, and an HTTP(S) `web_recharge_url`.
  Return the exact URL. If `--open` was requested, report whether `opened` is true.
- Exit `4`: APS returned the URL, but browser launch failed. Preserve the URL from stdout and
  report the safe `BROWSER_OPEN_FAILED` error from stderr so the user can open it manually.
- Other nonzero exits: report the safe JSON error from stderr; do not invent or reuse a URL.

`opened: false` is expected without `--open`. `opened: true` only means the operating system
accepted the browser-launch request. Neither a returned link nor a browser launch proves that the
page loaded, an order exists, or a payment succeeded. Leave all page interaction and payment to
the user.
