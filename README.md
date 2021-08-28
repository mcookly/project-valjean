<img src="web/src/static/img/svg/pv-logo-default.svg" alt="Logo" width="150px">

# Project Valjean
Project Valjean is an experimental app designed for rating the food at Notre Dame and understanding what foods are liked and disliked. Have any questions or comments?
Feel free to contact us at projvaljean@gmail.com.
### Screenshots (iPhone X)
---
#### Home
<img src="readme_images/home_ix.png" alt="Home" width="200px">

#### Rate
<img src="readme_images/rate_dh_ix.png" alt="Home" width="200px">
<img src="readme_images/rate_meal_ix.png" alt="Home" width="200px">
<img src="readme_images/rate_select_ix.png" alt="Home" width="200px">
<img src="readme_images/rate_rate_ix.png" alt="Home" width="200px">
<img src="readme_images/rate_done_ix.png" alt="Home" width="200px">

### Why?
We decided on the concept of a food-review system for Notre Dame’s dining halls because
1. the project appeared to be feasible given both the time constraint (about 1.5 months) and our skill level (knowing nothing about software dev),
2. we wanted a project that was in some ways useful or applicable, and
3. we saw the potential of upscaling the project if our attempts were successful.

### Approach
Our approach to the problem was fairly simple.
1. Scrape [Notre Dame’s meal webpage](nutrition.nd.edu/NetNutrition1) using the python web-scraper, [Scrapy](https://scrapy.org/).
2. Store the scraped data in a database.
3. Have the user scan a QR code to access the website. Once loaded, the user would be presented a form with a list of all the foods for the given day. 
4. The user would select the foods they ate and then rate them good or bad.
5. Store the user’s feedback in the database.
6. Present the user statistics on the food.
# Challenges
---
### Scraper
Our first problem quickly materialized from the fact that we had to scrape dynamic content off the website. Scrapy could only scrape static content, so we turned to another solution: the headless browser Splash since Selenium would be too heavy for our needs. Using the [Scrapy-Splash](https://github.com/scrapy-plugins/scrapy-splash) python library, we were able to configure a Scrapy spider that would load the dynamic content via mouse clicks and then scrape the food data. In the process, we had to learn some basic Lua, some basic html protocol, and how to identify specific web elements using CSS selectors and XPath.
### Docker
Splash can only be used as a Docker container, which would expose a port. Scrapy then can be configured to send its requests through this proxy. This presented no difficulties until we had to create a Docker image for the entire food scraper, which required Splash. Therefore, we needed two containers—Splash and the food scraper—to work together and communicate with each other. After hours of browsing scant documentation and vaguely-related StackOverflow questions, we came to understand that localhost on a Docker container remained only in that Docker container. The solution would be to create a Docker stack, name the Splash container “splash,” and route Scrapy’s spiders through http://splash:8050 rather than localhost. We first used Docker networks to test and debug the setup and then switched to Docker Compose to build the app stack for better testing.
### Web
We decided to use [Flask](https://flask.palletsprojects.com/en/2.0.x/) rather than Django because Flask is a microframework with less setup and configuration than Django. Configuring a web app on Flask was not difficult, especially when combined with [Material Design for Bootstrap](https://mdbootstrap.com/) for responsiveness and an appealing mobile layout, which we intend to be the primary device users choose. Since we had to pass data between web pages, we had three options: server-side cookies, client side cookies (Flask sessions), or dynamic routing. We chose dynamic routing since it provided less security vulnerabilities and better cross-platform reliability than cookies. The only difficulty involved figuring how to transport python dicts (the foods and their categories or reviews) through urls. This, we learned, could be solved using Flask's Json library to dump and load the dict.
### Database
Initially, we chose to use MySQL and store the data locally within a Docker stack. Once we realized that that structure would cost a lot more money than using the web host's own database structure, we opted to use Google's noSQL service [Firebase](https://firebase.google.com/). Setting up a database on Firebase took seconds; however, it required that we change code for our scraper's spiders. Initially, we ran a custom module that would be called after the food items for each meal were parsed. This would cycle through all the items and upload them to the database, but it would also call the client session for Firebase multiple times, which is not allowed/not good practice. Therefore, we opted to use Scrapy's Item and Pipeline system but again ran into a problem: Scrapy's items only seemed to be recognized by the Scrapy core if they were created within the spider file—not within our local module, where it would be easiest to configure. So we combined the two spiders—NDH and SDH—into one spider and generated each food item as it was scraped. Once an item was created, it would pass through the pipeline and be uploaded as a document to our Firestore database with a unique ID to prevent overwriting.
### What's left...
There is still much to be done—making the statistics page and running the app on Google Cloud, for instance. Unfortunately, both of us have started school again, so progress will slow down for now. We plan to be back in full swing this December.
