import re


def extract_title(response):
    for response_title in response.xpath('//h1[@class="firstHeading"]'):
        title = response_title.xpath('string()').extract()[0]

    return title


def extract_content(response, xpath):
    content = ''
    for node in response.xpath(xpath):
        if '<p>' in node.get()[:5]:
            content = content + node.xpath('string()').extract()[0]

    return content


def preprocess_content(content):
    # remove line breaks
    content = re.sub(r'\n', '', content)

    # remove all brackets
    content = re.sub(r'\(.*?\)', '', content)
    content = re.sub(r'\{.*?\}', '', content)
    content = re.sub(r"\[.*?\]", '', content)
    content = re.sub(r'\<.*?\>', '', content)

    # replace "
    content = re.sub(r'(\“)+|(\„)+|(\")', "'", content)

    # replace . after number (19. Oct -> 19 Oct)
    for match in re.finditer(r'\d+?\.', content):
        content = content.replace(match.group(), match.group().replace('.', ''))

    # remove all * (lists)
    content = re.sub(r'(\*+)', '', content)

    # remove multiple whitespaces
    content = re.sub(r'\s+', ' ', content)

    # remove whitespaces before and after string
    content = content.strip()

    return content
