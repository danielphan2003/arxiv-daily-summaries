# encoding: utf-8
import deserialize
import json
import os
import requests

from collections import namedtuple
from bs4 import BeautifulSoup as bs
from github import Github
from transformers import pipeline
from typing import Dict, List, Optional, Tuple

Paper = namedtuple("Paper", ["id", "title", "authors", "main_page", "tldr", "comments", "pdf"])

@deserialize.default("arxiv_base", "https://arxiv.org")
@deserialize.default("sub_url", "https://arxiv.org/list/cs/new")
@deserialize.default("tldr_max_length", 100)
@deserialize.default("model_name", "facebook/bart-base")
class Config:
    arxiv_base: str
    sub_url: str 
    keywords: List[str]
    tldr_max_length: int
    model_name: str

def sanitize_element(name: str, element: str) -> str:
    return element.text.replace(f"{name}:", " ").replace("\n", "").strip()

def get_arxiv_news(config: Config) -> Tuple[str, Dict[str, List[Paper]]]:
    summarizer = pipeline("summarization", config.model_name)
    
    summarize = lambda text: summarizer(text, max_length=config.tldr_max_length)

    page = requests.get(config.sub_url)
    soup = bs(page.text, "html.parser")
    content = soup.body.find("div", {'id': 'content'})

    issue_title = content.find("h3").text
    dt_list = content.dl.find_all("dt")
    dd_list = content.dl.find_all("dd")

    assert len(dt_list) == len(dd_list), "There should be a same amount of IDs compared to papers."

    sub = {key: [] for key in config.keywords}

    for idx, dd in enumerate(dd_list):
        abstract = sanitize_element("", dd.find("p", {"class": "mathjax"}))

        for keyword in config.keywords:
            if keyword.lower() in abstract.lower():
                id = dt_list[idx].text.strip().split(" ")[2].split(":")[-1]

                comments = dd.find("div", {"class": "list-comments"})

                sub[keyword].append(Paper(id,
                                        title = sanitize_element("Title", dd.find("div", {"class": "list-title mathjax"})),
                                        authors = sanitize_element("Authors", dd.find("div", {"class": "list-authors"})),
                                        main_page = f"{config.arxiv_base}/abs/{id}",
                                        tldr = summarize(abstract)[0]["summary_text"],
                                        comments = sanitize_element("Comments", comments) if comments else None,
                                        # abstract = abstract,
                                        pdf = f"{config.arxiv_base}/pdf/{id}"))

                break

    return issue_title, sub

def generate_full_report(config: Config, sub: Dict[str, List[Paper]]) -> str:
    format_comment = lambda comment: f"<strong>:sunflower: Comments:</strong> {paper.comments}<br>" if comment else ""

    full_report = ""

    for keyword in config.keywords:
        paper_count = len(sub[keyword])

        if paper_count == 0:
            continue
 
        full_report += f"<h2>Keyword: {keyword} ({paper_count} papers)</h2>"
 
        full_report += "<details>"
 
        for paper in sub[keyword]:
            # report = '### {}\n - **Authors:** {}\n - **Subjects:** {}\n - **Arxiv link:** {}\n - **Pdf link:** {}\n - **Abstract**\n {}' \
            #     .format(paper['title'], paper['authors'], paper['subjects'], paper['main_page'], paper['pdf'],
            #             paper['abstract'])
            report = f"<h3>{paper.title}</h3>\
                <strong>:brain: Authors:</strong> {paper.authors}<br>\
                <strong>:paw_prints: Details:</strong> <a href='{paper.main_page}'>arXiv:{paper.id}</a><br>\
                <strong>:ramen: tl;dr:</strong> {paper.tldr}...</a><br>\
                {format_comment(paper.comments)}\
                <a href='{paper.pdf}'>:seedling: Read more &#8594;</a><br>"
 
            full_report += report

        full_report += "</details>"

    return full_report
                                   
def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = deserialize.deserialize(Config, json.load(f))

    issue_title, sub = get_arxiv_news(config)

    full_report = generate_full_report(config, sub)

    # only make issue if at least one keyword has a new paper
    if full_report:
        # and if is running in GitHub Actions
        if os.environ['GITHUB_ACTIONS'] and os.environ['GITHUB_ACTIONS'] == "true":
            g = Github(os.environ['GITHUB_TOKEN'])
            user = os.environ['GITHUB_REPOSITORY_OWNER']
            repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
            issue = repo.create_issue(title=issue_title, body=full_report, assignee=user, labels=config.keywords)
        else:
            print(issue_title)
            print(full_report)

if __name__ == '__main__':
    main()
