import warnings
from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from gpt_researcher.utils.enum import ReportSource, ReportType, Tone

# Source verification constants
OFFICIAL_SOURCE_TYPES = {
    "government": ["linkedin.de", "handelsregister.de", ".at", "billiger.de", "trustedshops.de", ".de", "dnb.com", "https://www.unternehmensregister.de/ureg/search1.8.html" ,"northdata.de","reuters.de", "bloomberg.de", "https://opencorporates.com/advanced-search/", "com.", "handelsregister.de", "trustedshops.de", "billiger.de", "webvalid.de", "preisvergleich.de", "dnb.com", "https://www.unternehmensregister.de/ureg/search1.8.html" ,"northdata.de","reuters.de", "bloomberg.de", "https://opencorporates.com/advanced-search/"],
    "academic": [".edu", "scholar.google.com", "academic."],
    "corporate": ["linkedin.de", "com.", "handelsregister.de", "https://trustedshops.de", "billiger.de", "webvalid.de", "preisvergleich.de", "dnb.com", "https://www.unternehmensregister.de/ureg/search1.8.html" ,"https://northdata.de","reuters.de", "https://bloomberg.de", "https://dn.brandfetch.io", "https://opencorporates.com/advanced-search/"],
    "news": ["linkedin.de", "dnb.com", "https://www.unternehmensregister.de/ureg/search1.8.html" ,"northdata.de","reuters.de", "bloomberg.de", "dn.brandfetch.io", "https://opencorporates.com/advanced-search/"]
}

def verify_source_url(url: str) -> Dict[str, bool]:
    """Verify if a source URL is official and reliable.

    Args:
        url (str): The URL to verify

    Returns:
        Dict[str, bool]: Verification results
    """
    verification = {
        "is_official": any(domain in url.lower() for source_type in OFFICIAL_SOURCE_TYPES.values() for domain in source_type),
        "has_https": url.startswith("https://"),
        "is_primary_source": bool(url)  # Simplified check, expand based on needs
    }
    return verification

def generate_search_queries_prompt(
    question: str,
    parent_query: str,
    report_type: str,
    max_iterations: int = 3,
    context: str = ""
):
    """Generates the search queries prompt with emphasis on official sources.

    Args:
        question (str): The question to generate search queries for
        parent_query (str): The main question (for detailed reports)
        report_type (str): The report type
        max_iterations (int): Maximum number of search queries
        context (str): Context for better understanding

    Returns:
        str: Search queries prompt
    """
    if report_type in [ReportType.DetailedReport.value, ReportType.SubtopicReport.value]:
        task = f"{parent_query} - {question}"
    else:
        task = question

    source_requirements = """
    IMPORTANT SOURCE REQUIREMENTS:
    1. Prioritize official and authoritative sources:
       - the clients website {URL} need to be checked for imprint and impressum search there for name of company, company ID, CEO (Inhaber) address, tags, phone and telephone. As well use the companies websites for any logo image that u find and take the URL of that, check with highest importance, for the logo url always https://cdn.brandfetch.io/      followed by the company url, so for example for dci.de you will type: https://cdn.brandfetch.io/dci.de and give us the link in your result.
       - comapny websites (.com, .net, billiger.de, bloomberg.de, trustedshops.de, guenstiger.de, handelsregister.de, dnb.com, northdata.de, webvalid.de)
       - Educational institutions (.edu)
       - Official company websites and investor relations
       - Reputable news organizations
       - Peer-reviewed academic sources
    2. Verify source credibility:
       - Check publication dates for currency, make sure it is the exact company
       - Confirm author credentials and dont fall into fake news
       - Validate institutional affiliations
    3. Avoid:
       - Unofficial blogs or personal websites
       - Social media posts
       - Forums or discussion boards
       - Unverified news sources
       - bild.de, express.de, fakenews
    """

    context_prompt = f"""
    Context: {context}

    Use this context to inform and refine your search queries. The context provides real-time web information that can help you generate more specific and relevant queries. Consider any current events, recent developments, or specific details mentioned in the context that could enhance the search queries.
    """ if context else ""

    dynamic_example = ", ".join([f'"query {i+1}"' for i in range(max_iterations)])

    return f"""Write {max_iterations} google search queries to search online that form an objective opinion from the following task: "{task}"

    Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

    {source_requirements}

    {context_prompt}
    You must respond with a list of strings in the following format: [{dynamic_example}].
    The response should contain ONLY the list.
    """

def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
):
    """Generates report prompt with strict source verification requirements."""

    source_verification_requirements = """
    STRICT SOURCE VERIFICATION REQUIREMENTS:
    1. Only use information from verified official sources check on the exact company name and verify that info 3 times
    2. Cross-reference all facts with multiple reliable sources
    3. Clearly distinguish between official statements and analysis
    4. Include source credibility assessment for each reference
    5. Note any conflicting information between sources
    6. Indicate when information comes from primary vs secondary sources
    7. Flag any unverified claims or potential misinformation
    8. Do not mix up different companies or entities
    9. Verify dates and temporal context of all information
    10. Include official document or report numbers where applicable
    11. Check always the official company name as your first source of information, including, Name of Company, Description, URL of Logo, Tags (5 only for category),
    """

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
        You MUST write all used source urls at the end of the report as references, and:
        1. Verify each source's authenticity and authority
        2. Include source verification status
        3. Note official vs unofficial sources
        4. Add publication dates for temporal context
        5. Include author credentials where available
        6. Note institutional affiliations
        7. Hyperlink format: [url website](url)

        Citation format example:
        Author, A. A. (Year, Month Date). Title of web page. Official Organization Name. [url website](url)
        [Source Type: Official/Academic/Corporate] [Verification Status: Verified/Pending]
        """
    else:
        reference_prompt = f"""
        You MUST write all used source document names at the end of the report as references, and:
        1. Verify document authenticity
        2. Include document classification level
        3. Note official status
        4. Add publication dates
        5. Include author credentials
        6. Note organizational authority
        """

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""

    return f"""
    Information: "{context}"
    ---
    Using the above information, answer the following query or task: "{question}" in a detailed report --
    The report should focus on the answer to the query, should be well structured, informative, 
    in-depth, and comprehensive, with facts and numbers if available and at least {total_words} words.

    {source_verification_requirements}

    Please follow all of the following guidelines in your report:
    - You MUST determine your own concrete and valid opinion based ONLY on verified information from official sources
    - You MUST write the report with markdown syntax and {report_format} format
    - You MUST prioritize official sources in this order:
        1. Government and regulatory documents
        2. Official company filings and statements
        3. Academic and research publications
        4. Reputable news organizations
    - You must verify dates and temporal context for all information
    - Use in-text citation references in {report_format} format with source verification status
    - Don't forget to add a reference list with full verification details
    - {reference_prompt}
    - {tone_prompt}

    Please do your best, this database is used officially by millions of people.
    Assume that the current date is {date.today()}.
    """



def generate_resource_report_prompt(
    question, context, report_source: str, report_format="apa", tone=None, total_words=1000
):
    """Generates the resource report prompt for the given question and research summary.

    Args:
        question (str): The question to generate the resource report prompt for.
        context (str): The research summary to generate the resource report prompt for.

    Returns:
        str: The resource report prompt for the given question and research summary.
    """

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
            You MUST include all relevant source urls.
            Every url should be hyperlinked: [url website](url)
            """
    else:
        reference_prompt = f"""
            You MUST write all used source document names at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each."
        """

    return (
        f'"""{context}"""\n\nBased on the above information, generate a bibliography recommendation report for the following'
        f' question or topic: "{question}". The report should provide a detailed analysis of each recommended resource,'
        " explaining how each source can contribute to finding answers to the research question.\n"
        "Focus on the relevance, reliability, and significance of each source.\n"
        "Ensure that the report is well-structured, informative, in-depth, and follows Markdown syntax.\n"
        "Include relevant facts, figures, and numbers whenever available.\n"
        f"The report should have a minimum length of {total_words} words.\n"
        "You MUST include all relevant source urls."
        "Every url should be hyperlinked: [url website](url)"
        f"{reference_prompt}"
    )


def generate_custom_report_prompt(
    query_prompt, context, report_source: str, report_format="apa", tone=None, total_words=1000
):
    return f'"{context}"\n\n{query_prompt}'


def generate_outline_report_prompt(
    question, context, report_source: str, report_format="apa", tone=None,  total_words=1000
):
    """Generates the outline report prompt for the given question and research summary.
    Args: question (str): The question to generate the outline report prompt for
            research_summary (str): The research summary to generate the outline report prompt for
    Returns: str: The outline report prompt for the given question and research summary
    """

    return (
        f'"""{context}""" Using the above information, generate an outline for a research report in Markdown syntax'
        f' for the following question or topic: "{question}". The outline should provide a well-structured framework'
        " for the research report, including the main sections, subsections, and key points to be covered."
        f" The research report should be detailed, informative, in-depth, and a minimum of {total_words} words."
        " Use appropriate Markdown syntax to format the outline and ensure readability."
    )


def get_report_by_type(report_type: str):
    report_type_mapping = {
        ReportType.ResearchReport.value: generate_report_prompt,
        ReportType.ResourceReport.value: generate_resource_report_prompt,
        ReportType.OutlineReport.value: generate_outline_report_prompt,
        ReportType.CustomReport.value: generate_custom_report_prompt,
        ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
    }
    return report_type_mapping[report_type]


def auto_agent_instructions():
    return """
This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific server, defined by its type and role, with each server requiring distinct instructions.
Agent
The server is determined by the field of the topic and the specific name of the server that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each server type is associated with a corresponding emoji.

examples:
task: "should I invest in apple stocks?"
response: 
{
    "server": "💰 Finance Agent",
    "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
}
task: "could reselling sneakers become profitable?, give me info about company LLC,company.com,Michael Mohr, dci.de,DCI AG,Michael Mohr"
response: 
{ 
    "server":  "📈 Business Analyst Agent",
    "agent_role_prompt": "You are an experienced AI business analyst expert, your job is to fill our Database with the most usefull information  about the company i ask for, please give me just the information without long sentences. Only follow this format:
    Name of Company
    Address incl. Street, Zip Code, City, Country
    Phone Number
    Email Address
    CEO (Name one or multiple)
    Tags of Company (5 of Company Category)
    Logo-URL (found from the website of company or trustedshops.de)
    Image URL from Google Images any Pressphotos official
    Description of Company (max 5 Sentences) history and present activity
    Tech Stacks (as much as u can find)
    Financial (if available)
    News from Google News (last 5 news about the company)
    Future Prediction (possible deal with company in which field)
    How likely is it to get a contract with that company in % from 0-100
    . Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
}
task: "what are the most interesting sites in Tel Aviv?"
response:
{
    "server:  "🌍 Travel Agent",
    "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
}
"""


def generate_summary_prompt(query, data):
    """Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return (
        f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the '
        f"query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual "
        f"information such as numbers, stats, quotes, etc if available. "
    )


################################################################################################

# DETAILED REPORT PROMPTS


def generate_subtopics_prompt() -> str:
    return """
Provided the main topic:

{task}

and research data:

{data}

- Construct a list of subtopics which indicate the headers of a report document to be generated on the task. 
- These are a possible list of subtopics : {subtopics}.
- There should NOT be any duplicate subtopics.
- Limit the number of subtopics to a maximum of {max_subtopics}
- Finally order the subtopics by their tasks, in a relevant and meaningful order which is presentable in a detailed report

"IMPORTANT!":
- Every subtopic MUST be relevant to the main topic and provided research data ONLY!

{format_instructions}
"""


def generate_subtopic_report_prompt(
    current_subtopic,
    existing_headers: list,
    relevant_written_contents: list,
    main_topic: str,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
) -> str:
    return f"""
Context:
"{context}"

Main Topic and Subtopic:
Using the latest information available, construct a detailed report on the subtopic: {current_subtopic} under the main topic: {main_topic}.
You must limit the number of subsections to a maximum of {max_subsections}.

Content Focus:
- The report should focus on answering the question, be well-structured, informative, in-depth, and include facts and numbers if available.
- Use markdown syntax and follow the {report_format.upper()} format.

IMPORTANT:Content and Sections Uniqueness:
- This part of the instructions is crucial to ensure the content is unique and does not overlap with existing reports.
- Carefully review the existing headers and existing written contents provided below before writing any new subsections.
- Prevent any content that is already covered in the existing written contents.
- Do not use any of the existing headers as the new subsection headers.
- Do not repeat any information already covered in the existing written contents or closely related variations to avoid duplicates.
- If you have nested subsections, ensure they are unique and not covered in the existing written contents.
- Ensure that your content is entirely new and does not overlap with any information already covered in the previous subtopic reports.

"Existing Subtopic Reports":
- Existing subtopic reports and their section headers:

    {existing_headers}

- Existing written contents from previous subtopic reports:

    {relevant_written_contents}

"Structure and Formatting":
- As this sub-report will be part of a larger report, include only the main body divided into suitable subtopics without any introduction or conclusion section.

- You MUST include markdown hyperlinks to relevant source URLs wherever referenced in the report, for example:

    ### Section Header
    
    This is a sample text. ([url website](url))

- Use H2 for the main subtopic header (##) and H3 for subsections (###).
- Use smaller Markdown headers (e.g., H2 or H3) for content structure, avoiding the largest header (H1) as it will be used for the larger report's heading.
- Organize your content into distinct sections that complement but do not overlap with existing reports.
- When adding similar or identical subsections to your report, you should clearly indicate the differences between and the new content and the existing written content from previous subtopic reports. For example:

    ### New header (similar to existing header)

    While the previous section discussed [topic A], this section will explore [topic B]."

"Date":
Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

"IMPORTANT!":
- The focus MUST be on the main topic! You MUST Leave out any information un-related to it!
- Must NOT have any introduction, conclusion, summary or reference section.
- You MUST include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
- You MUST mention the difference between the existing content and the new content in the report if you are adding the similar or same subsections wherever necessary.
- The report should have a minimum length of {total_words} words.
- Use an {tone.value} tone throughout the report.

Do NOT add a conclusion section.
"""


def generate_draft_titles_prompt(
    current_subtopic: str,
    main_topic: str,
    context: str,
    max_subsections: int = 5
) -> str:
    return f"""
"Context":
"{context}"

"Main Topic and Subtopic":
Using the latest information available, construct a draft section title headers for a detailed report on the subtopic: {current_subtopic} under the main topic: {main_topic}.

"Task":
1. Create a list of draft section title headers for the subtopic report.
2. Each header should be concise and relevant to the subtopic.
3. The header should't be too high level, but detailed enough to cover the main aspects of the subtopic.
4. Use markdown syntax for the headers, using H3 (###) as H1 and H2 will be used for the larger report's heading.
5. Ensure the headers cover main aspects of the subtopic.

"Structure and Formatting":
Provide the draft headers in a list format using markdown syntax, for example:

### Header 1
### Header 2
### Header 3

"IMPORTANT!":
- The focus MUST be on the main topic! You MUST Leave out any information un-related to it!
- Must NOT have any introduction, conclusion, summary or reference section.
- Focus solely on creating headers, not content.
"""


def generate_report_introduction(question: str, research_summary: str = "") -> str:
    return f"""{research_summary}\n 
Using the above latest information, Prepare a detailed report introduction on the topic -- {question}.
- The introduction should be succinct, well-structured, informative with markdown syntax.
- As this introduction will be part of a larger report, do NOT include any other sections, which are generally present in a report.
- The introduction should be preceded by an H1 heading with a suitable topic for the entire report.
- You must include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
Assume that the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.
"""


def generate_report_conclusion(query: str, report_content: str) -> str:
    """
    Generate a concise conclusion summarizing the main findings and implications of a research report.

    Args:
        report_content (str): The content of the research report.

    Returns:
        str: A concise conclusion summarizing the report's main findings and implications.
    """
    prompt = f"""
    Based on the research report below and research task, please write a concise conclusion that summarizes the main findings and their implications:
    
    Research task: {query}
    
    Research Report: {report_content}

    Your conclusion should:
    1. Recap the main points of the research
    2. Highlight the most important findings
    3. Discuss any implications or next steps
    4. Be approximately 2-3 paragraphs long
    
    If there is no "## Conclusion" section title written at the end of the report, please add it to the top of your conclusion. 
    You must include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
    
    Write the conclusion:
    """

    return prompt


report_type_mapping = {
    ReportType.ResearchReport.value: generate_report_prompt,
    ReportType.ResourceReport.value: generate_resource_report_prompt,
    ReportType.OutlineReport.value: generate_outline_report_prompt,
    ReportType.CustomReport.value: generate_custom_report_prompt,
    ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
}


def get_prompt_by_report_type(report_type):
    prompt_by_type = report_type_mapping.get(report_type)
    default_report_type = ReportType.ResearchReport.value
    if not prompt_by_type:
        warnings.warn(
            f"Invalid report type: {report_type}.\n"
            f"Please use one of the following: {', '.join([enum_value for enum_value in report_type_mapping.keys()])}\n"
            f"Using default report type: {default_report_type} prompt.",
            UserWarning,
        )
        prompt_by_type = report_type_mapping.get(default_report_type)
    return prompt_by_type

