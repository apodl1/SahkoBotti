## SähköBotti

A Telegram bot for getting the coming spot price of electricity in Finland. Running instance can be found at [t.me/elektroniBot](https://t.me/elektroniBot) or with nick @elektroniBot on Telegram.

Data supplied by the ENTSO-E Transparency Platform (transparency.entsoe.eu).

### Why this and not the other innumerable electricity price display solutions?
- **Fast**. Sub-1s response time on average. No more loading web-pages, cookies or analytics.
- **Only shows coming prices**. No more searching for the current price among historical data.
- **Constant visualization scale**. Know if it is cheap or expensive at a glance without checking out the axis markings.
- **Time-to-price display**. Know exactly what to set your dishwasher timer to wihtout mental math.
- **Private**. No analytics collected (check out for yourself in the source code ;) )

Example response:
<br>
<picture>
    <source srcset="https://github.com/apodl1/SahkoBotti/blob/master/screenshot.png">
    <img alt="Screenshot" src="https://github.com/apodl1/SahkoBotti/blob/master/screenshot.png" width="350">
</picture>

Requires a Telegram bot and ENTSO-E API-tokens in directory root to run yourself. Files have to be named ".telegram_token" and ".entsoe_token" respectively.
