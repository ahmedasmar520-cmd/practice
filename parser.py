import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://www.google.com/maps?hl=en")
time.sleep(4)

search_box = driver.find_element(By.CSS_SELECTOR, 'input#searchboxinput, input[name="q"]')
search_box.click()
search_box.send_keys("restaurants in Lahore")
search_box.send_keys(Keys.ENTER)

while not driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"]'):
    time.sleep(1)

panel = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')

while len(driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")) < 40:
    panel.send_keys(Keys.END)
    time.sleep(1.5)

def get_text(parent, selector):
    try:
        return " ".join(parent.find_element(By.CSS_SELECTOR, selector).get_attribute("textContent").split())
    except:
        return "N/A"

def get_attr(parent, selector, attr):
    try:
        return parent.find_element(By.CSS_SELECTOR, selector).get_attribute(attr)
    except:
        return "N/A"

results = []

for i in range(40):
    cards = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
    if i >= len(cards):
        break

    card = cards[i]
    link = card.get_attribute("href")

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
    driver.execute_script("arguments[0].click();", card)
    time.sleep(2.5)

    try:
        overview_btn = driver.find_element(By.CSS_SELECTOR, 'button[role="tab"][aria-label*="Overview"]')
        driver.execute_script("arguments[0].click();", overview_btn)
        time.sleep(1)
    except:
        pass

    timings = {}
    for row in driver.find_elements(By.CSS_SELECTOR, "table.eK4R0e tr.y0skZc, table.eK4R0e tr"):
        day = get_text(row, "td.ylH6lf, td:first-child")
        hours = get_text(row, "td.mxowUb, td:last-child")
        if day != "N/A":
            timings[day] = hours

    avg_price = "N/A"
    for sp in driver.find_elements(By.CSS_SELECTOR, 'span[aria-label*="Price"], span.mgr77e'):
        txt = " ".join(sp.get_attribute("textContent").split()).lstrip("· ").strip()
        if "Rs" in txt or "$" in txt or "PKR" in txt:
            avg_price = txt
            break

    item = {
        "name": get_text(driver, "h1.DUwDvf"),
        "food_type": get_text(driver, "button.DkEaL"),
        "rating": get_text(driver, 'div.F7nice span[aria-hidden="true"]'),
        "avg_price_per_head": avg_price,
        "service_options": get_text(driver, "div.E0DTEd"),
        "location": get_text(driver, 'button[data-item-id="address"] div.fontBodyMedium'),
        "phone": get_text(driver, 'button[data-item-id^="phone"] div.fontBodyMedium'),
        "website": get_attr(driver, 'a[data-item-id="authority"]', "href"),
        "maps_link": link,
        "weekly_timings": timings,
        "reviews": []
    }

    try:
        rev_tab = driver.find_element(By.CSS_SELECTOR, 'button[role="tab"][aria-label*="Reviews"]')
        driver.execute_script("arguments[0].click();", rev_tab)
        time.sleep(2.5)

        for pane in driver.find_elements(By.CSS_SELECTOR, "div.m6QErb.DxyBCb"):
            driver.execute_script("arguments[0].scrollTop = 600;", pane)
        time.sleep(1.5)
    except:
        pass

    for rev in driver.find_elements(By.CSS_SELECTOR, "div.jftiEf[data-review-id]")[:5]:
        try:
            for btn in rev.find_elements(By.CSS_SELECTOR, "button.w8nwRe.kyuRq"):
                driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.3)
        except:
            pass

        rev_price = "N/A"
        for block in rev.find_elements(By.CSS_SELECTOR, "div.PBK6be"):
            b_text = " ".join(block.get_attribute("textContent").split())
            if "Price per person" in b_text or "Rs" in b_text or "PKR" in b_text:
                rev_price = b_text.replace("Price per person", "").strip(" :·")
                break

        item["reviews"].append({
            "author": get_text(rev, "div.d4r55"),
            "rating": get_attr(rev, 'span.kvMYJc, span[role="img"][aria-label*="star"]', "aria-label"),
            "date": get_text(rev, "span.rsqaWe"),
            "avg_price_per_head": rev_price,
            "text": get_text(rev, "span.wiI7pd")
        })

    results.append(item)

    with open("restaurants.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(results, indent=4, ensure_ascii=False))

    print(f"Saved #{len(results)}: {item['name']} (Reviews: {len(item['reviews'])})")

driver.quit()