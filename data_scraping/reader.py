from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as et
import json as js


class UnhandledException(Exception):
    pass

def get_text_or_default(element, default=""):
    """
    Helper function to safely get text from an XML element.
    Returns a default value if the element is None.
    """
    return element.text if element is not None else default


def rss_parser(
    xml: str,
    limit: Optional[int] = None,
    json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        '>>> xml = '<rss><channel><title>Some RSS Channel</title><link>https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        ">>> rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        ">>> print("\\n".join(rss_parser(xmls)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """
    #formating XML file into string
    xml_str = et.fromstring(xml)
    #findinf <chanel> elements if they exist
    channel = xml_str.find("channel")
    if channel is None:
        raise UnhandledException("No <channel> found in the RSS feed.")

    # extraxt information with default values
    channel_info = {
        "title": get_text_or_default(channel.find("title"),""),
        "link": get_text_or_default(channel.find("link"),""),
        "description": get_text_or_default(channel.find("description"),""),
        "lastBuildDate": get_text_or_default(channel.find("lastBuildDate"),""),
        "pubDate": get_text_or_default(channel.find("pubDate"),""),
        "language": get_text_or_default(channel.find("language"),""),
        "categories": [category.text for category in channel.findall("category")] or [],
        "managingEditor": get_text_or_default(channel.find("managingEditor"),""),
    }

    # Extract items with default values
    items = []
    for item in channel.findall("item"):
        item_info = {
            "title": get_text_or_default(item.find("title"),""),
            "author": get_text_or_default(item.find("author"),""),
            "pubDate": get_text_or_default(item.find("pubDate"),""),
            "link": get_text_or_default(item.find("link"),""),
            "categories": [category.text for category in item.findall("category")] or [],
            "description": get_text_or_default(item.find("description"),""),
        }
        items.append(item_info)

    # Checking if there is a limit and applying it
    if limit is not None:
        items = items[:limit]

    #output --json
    if json:
        json_output = {
            "title": channel_info["title"],
            "link": channel_info["link"],
            "description": channel_info["description"],
            "items": [
                {
                    "title": item["title"],
                    "author": item["author"],
                    "pubDate": item["pubDate"],
                    "link": item["link"],
                    "categories": item["categories"],
                    "description": item["description"],
                }
                for item in items
            ]
        }
        return [js.dumps(json_output, indent=2)]

    # standard output; paste optional arguments only if they
    result = []

    # channel output
    result.append(f"Feed: {channel_info['title']}")
    result.append(f"Link: {channel_info['link']}")
    if not channel_info['lastBuildDate'] == "":
        result.append(f"Last Build Date: {channel_info['lastBuildDate']}")
    if not channel_info['pubDate'] == "":
        result.append(f"Publish Date: {channel_info['pubDate']}" )
    if not channel_info['language'] == "":
        result.append(f"Language: {channel_info['language']}")
    if not len(channel_info["categories"]) == 0:
        result.append(f"Categories: {', '.join(channel_info['categories'])}")
    if not channel_info['managingEditor'] == "":
        result.append(f"Editor: {channel_info['managingEditor']}")
    if not channel_info['description'] == "":
        result.append(f"Description: {channel_info['description']}" )

    #blank line
    result.append("")

    # item output
    for item in items:
        result.append(f"Title: {item['title']}" )
        if not item['author']=="":
            result.append(f"Author: {item['author']}" if not item["author"] == "" else "")
        if not item['pubDate']=="" :
            result.append(f"Published: {item['pubDate']}" if not item["pubDate"] == "" else "")
        result.append(f"Link: {item['link']}" )
        if not len(item["categories"]) ==0:
            result.append(f"Categories: {', '.join(item['categories'])}")
        result.append(item["description"] )

    return result

def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    xml = requests.get(args.source).text



    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()
