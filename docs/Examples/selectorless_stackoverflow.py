"""
I only made this example to show how Scrapling features can be used to scrape a website without writing any selector
    so this script doesn't depend on the website structure.
"""

import requests
from scrapling import Adaptor

response = requests.get('https://stackoverflow.com/questions/tagged/web-scraping?sort=MostVotes&filters=NoAcceptedAnswer&edited=true&pagesize=50&page=2')
page = Adaptor(response.text, url=response.url)
# First we will extract the first question title and its author based on the text content
first_question_title = page.find_by_text('Run Selenium Python Script on Remote Server')
first_question_author = page.find_by_text('Ryan')
# because this page changes a lot
if first_question_title and first_question_author:
    # If you want you can extract other questions tags like below
    first_question = first_question_title.find_ancestor(
        lambda ancestor: ancestor.attrib.get('id') and 'question-summary' in ancestor.attrib.get('id')
    )
    rest_of_questions = first_question.find_similar()
    # But since nothing to rely on to extract other titles/authors from these elements without CSS/XPath selectors due to the website nature
    # We will get all the rest of the titles/authors in the page depending on the first title and the first author we got above as a starting point
    for i, (title, author) in enumerate(zip(first_question_title.find_similar(), first_question_author.find_similar()), start=1):
        print(i, title.text, author.text)

