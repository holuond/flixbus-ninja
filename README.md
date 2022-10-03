# Flixbus Ninja 🐱‍👤

This is a simple app useful when your desired Flixbus connection is fully booked and you'd like to maximize your chances
of getting on board if someone cancels their reservation.

The app opens a browser and evaluates the current state of your connection(s) and whether there are enough free seats to
satisfy your request. If so, the reservation page is opened (otherwise the browser closes and the application run ends).
It is then left to you to manually finish the reservation process. The requested seats are protected for at least 5
minutes after opening the reservation page, so you can finalize the transaction in peace.

https://user-images.githubusercontent.com/64732928/193884806-2ffad75a-6859-4be9-a4ca-027b942b23c1.mp4

Developed for `shop.flixbus.cz` and the `cs` locale (which affects aspects such as datetime formatting etc.), but it
should be easily customizable for other country+language variations of the website.

## Usage

Customize the `conf/application.yaml` configuration file and run:

```bash
poetry install -n
poetry run playwright install
poetry run python flixbus_ninja
```

You can periodically run the app in an automated fashion by using an orchestration tool like cron (or scheduled tasks on
Windows).
