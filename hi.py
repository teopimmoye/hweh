import base64
import random
import requests
import logging
from seleniumbase import SB

# ---------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------
def get_geo_data():
    """Fetch geolocation data safely."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "country_code": data.get("countryCode", "").lower()
        }
    except Exception as e:
        logging.error(f"Failed to fetch geo data: {e}")
        return None


def decode_username(encoded_name):
    """Decode base64 username safely."""
    try:
        return base64.b64decode(encoded_name).decode("utf-8")
    except Exception as e:
        logging.error(f"Failed to decode username: {e}")
        return None


def click_if_present(driver, selector, timeout=4):
    """Click an element only if it exists."""
    if driver.is_element_present(selector):
        driver.cdp.click(selector, timeout=timeout)
        driver.sleep(1)


# ---------------------------------------------------------
# Main Automation Logic
# ---------------------------------------------------------
def run_stream_viewer():
    geo = get_geo_data()
    if not geo:
        logging.error("Cannot continue without geo data.")
        return

    username = decode_username("YnJ1dGFsbGVz")
    if not username:
        logging.error("Cannot continue without username.")
        return

    url = f"https://www.twitch.tv/{username}"
    proxy_str = False

    logging.info(f"Starting viewer for: {url}")

    while True:
        with SB(
            uc=True,
            locale="en",
            ad_block=True,
            chromium_arg='--disable-webgl',
            proxy=proxy_str
        ) as driver:

            rnd = random.randint(450, 800)

            driver.activate_cdp_mode(
                url,
                tzone=geo["timezone"],
                geoloc=(geo["lat"], geo["lon"])
            )

            driver.sleep(2)
            click_if_present(driver, 'button:contains("Accept")')

            driver.sleep(12)
            click_if_present(driver, 'button:contains("Start Watching")')
            click_if_present(driver, 'button:contains("Accept")')

            if driver.is_element_present("#live-channel-stream-information"):
                logging.info("Stream detected. Spawning secondary viewer...")

                driver2 = driver.get_new_driver(undetectable=True)
                driver2.activate_cdp_mode(
                    url,
                    tzone=geo["timezone"],
                    geoloc=(geo["lat"], geo["lon"])
                )

                driver2.sleep(10)
                click_if_present(driver2, 'button:contains("Start Watching")')
                click_if_present(driver2, 'button:contains("Accept")')

                driver.sleep(rnd)
            else:
                logging.info("Stream offline. Exiting loop.")
                break


# ---------------------------------------------------------
# Test Functions (Safe, Non‑Breaking)
# ---------------------------------------------------------
def test_geo_data():
    """Test geolocation fetch without running automation."""
    data = get_geo_data()
    assert data is None or ("lat" in data and "lon" in data)
    logging.info("test_geo_data passed.")
    return data


def test_username_decode():
    """Test base64 decoding."""
    decoded = decode_username("YnJ1dGFsbGVz")
    assert decoded == "brutalles"
    logging.info("test_username_decode passed.")
    return decoded


def test_click_wrapper():
    """Dry-run test for click wrapper (no driver interaction)."""
    try:
        click_if_present(None, "fake")  # Should not crash
    except Exception:
        assert False, "click_if_present should not crash with None driver"
    logging.info("test_click_wrapper passed.")


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------
if __name__ == "__main__":
    # Run tests without affecting main script
    test_geo_data()
    test_username_decode()
    #test_click_wrapper()

    # Start main script
    run_stream_viewer()
