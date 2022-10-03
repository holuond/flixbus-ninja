from dataclasses import dataclass
from pprint import pprint

from playwright.sync_api import sync_playwright, ElementHandle

from config import Config


@dataclass
class RideSearchResult:
    departure_time: str
    departure_station: str
    destination_station: str
    element_handle: ElementHandle


def run() -> None:
    """Opens the Flixbus shop, finds the optimal connection (ride) based on the user-specified config, and steps into
    the reservation dialog, letting the user pick it up from there and finalize their reservation."""
    BASE_URL = 'https://shop.flixbus.cz/search'

    # Load the configuration file
    config = Config.from_yaml('conf/application.yaml')
    pprint(config)

    with sync_playwright() as p:
        # Set up Playwright and obtain the Flixbus shop search page based on the specified ride params
        request_params = {'departureCity': config.departure_city,
                          'arrivalCity': config.destination_city,
                          'rideDate': config.departure_date} | config.passengers
        url = BASE_URL + '?' + ''.join([f'&{param}={value}' for (param, value) in request_params.items()])
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.click('button[data-testid="uc-deny-all-button"]')  # Cookie consent banner

        # Identify all rides for the specified date
        found_rides = []
        for result_item in page.query_selector_all('div[data-e2e*="search-result-item"]'):
            found_rides.append(RideSearchResult(
                result_item.query_selector('div[data-e2e*="search-result-departure-time"]').inner_text(),
                result_item.query_selector('div[data-e2e*="search-result-departure-station"]').inner_text(),
                result_item.query_selector('div[data-e2e*="search-result-arrival-station"]').inner_text(),
                result_item
            ))

        # Filter out rides not desired by the user and order by priority
        def desired_by_user(ride: RideSearchResult) -> bool:
            return \
                (ride.departure_time in config.departure_times_ordered_by_priority and
                 ride.departure_station == config.departure_station and
                 ride.destination_station == config.destination_station)

        desired_rides: list = [ride for ride in found_rides if desired_by_user(ride)]

        # Print a warning when the user-specified ride configuration doesn't match the search results
        if len(desired_rides) != len(config.departure_times_ordered_by_priority):
            print("WARN: The number of rides you've specified is not equal to the amount of found, matching rides. "
                  "Perhaps you've made a configuration error?")
            print('Matching rides:')
            print([ride.departure_time for ride in desired_rides])

        # Filter out fully booked rides
        desired_rides_with_free_seats = [ride for ride in desired_rides if not ride.element_handle.query_selector(
            'div[data-e2e="search-result-fully-booked-message"]')]

        dep_time_to_priority: dict[str, int] = {dep_time: priority for priority, dep_time in
                                                enumerate(config.departure_times_ordered_by_priority, start=1)}
        desired_rides_prioritized = sorted(desired_rides_with_free_seats,
                                           key=lambda ride: dep_time_to_priority[ride.departure_time])

        # Identify the best ride
        if desired_rides_prioritized:
            best_ride: RideSearchResult = desired_rides_prioritized[0]
        else:
            print("No ride with enough free seats was found. Quitting.")
            browser.close()
            return

        # Open the reservation
        print(f"Selecting the highest-priority ride with free seats: {best_ride.departure_time}")
        best_ride.element_handle.query_selector('button[data-e2e="button-reserve-trip"]').click()
        page.wait_for_timeout(30 * 60 * 1000)  # Leave the browser open and allow the user to finalize the reservation


if __name__ == '__main__':
    run()
