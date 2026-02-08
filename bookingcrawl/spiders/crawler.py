import scrapy
import asyncio

class CrawlerSpider(scrapy.Spider):
    scraped_titles = set()
    name = "crawler"
    url = "https://www.booking.com/searchresults.de.html?ss=Berlin%2C+Deutschland&efdco=1&label=gen173nr-10CAEoggI46AdIM1gEaDuIAQGYATO4ARfIAQ_YAQPoAQH4AQGIAgGoAgG4AvCLjswGwAIB0gIkOTFhZWVkMzYtM2VhMS00NzhjLWIyYzktOWY5NGIzOGMzODlh2AIB4AIB&aid=304142&lang=de&sb=1&src_elem=sb&src=index&dest_id=-1746443&dest_type=city&group_adults=2&no_rooms=1&group_children=0"

    page_count = 10 # Enter how much load more clicks you want

    headers = {
        "Accept": "*/*",
        "Accept-Language": "de-DE,de;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Referer": "https://www.booking.com/",
    }

    def build_request(self):
        return scrapy.Request(url=self.url, callback=self.parse, headers=self.headers, meta={"playwright": True, "playwright_include_page": True})

    async def start(self):
        yield self.build_request()

    async def scrolling(self, page):
        await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)

    async def parse(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.click("#onetrust-reject-all-handler", timeout=2000)
            await page.click("button[aria-label*='Informationen zur Anmeldung ausblenden.']", timeout=2000)
        except:
            pass

        button_path = "button:has-text('Weitere Suchergebnisse laden')"

        for i in range(self.page_count):
            current_count = await page.locator("//div[@data-testid='property-card']").count()

            await self.scrolling(page)

            load_more_button = page.locator(button_path)

            if await load_more_button.is_visible():
                try:
                    await load_more_button.scroll_into_view_if_needed()
                    await asyncio.sleep(1)

                    await load_more_button.click()

                    try:
                        await page.wait_for_timeout(2000)  # Wait for request to start
                        await page.locator("div[data-testid='property-card']").nth(current_count).wait_for(
                            timeout=15000)
                        await asyncio.sleep(1)

                    except Exception as timeout_err:
                        new_count = await page.locator("//div[@data-testid='property-card']").count()
                        if new_count > current_count:
                            self.logger.info(f"✓ Content loaded despite timeout: {current_count} → {new_count}")
                        else:
                            self.logger.warning(f"✗ No new content loaded")

                except Exception as e:
                    self.logger.error(f"✗ Error clicking button: {e}")
                    break
            else:
                self.logger.info("✗ 'Load more' button not visible")
                await self.scrolling(page)
                if not await load_more_button.is_visible():
                    self.logger.info("Button still not visible - reached end")
                    break

        content = await page.content()
        selector = scrapy.Selector(text=content)
        items = selector.xpath("//div[@data-testid='property-card']")

        for item in items:
            title = item.xpath(".//div[@data-testid='title']/text()").get()

            if not title or title.strip() in self.scraped_titles:
                continue

            self.scraped_titles.add(title.strip())

            yield {
                "title": title.strip(),
                "address": item.xpath(".//span[@data-testid='address']/text()").get(default="N/A"),
                "distance": item.xpath(".//span[@data-testid='distance']/text()").get(default="N/A").strip(),
                "rating": item.xpath(".//div[contains(text(), 'Bewertet mit ')]/text()").get(default="N/A").replace(
                    "Bewertet mit ", "").strip(),
                "link": item.xpath(".//a[@data-testid='title-link']/@href").get(default="N/A"),
            }
        await page.close()