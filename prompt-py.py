import warnings
from datetime import date, datetime, timezone

from ..utils.enum import ReportSource, ReportType, Tone

def generate_search_queries_prompt(
    question: str,
    parent_query: str,
    report_type: str,
    max_iterations: int = 3,
):
    """Generates search queries prompt focusing on official sources."""
    if (
        report_type == ReportType.DetailedReport.value
        or report_type == ReportType.SubtopicReport.value
    ):
        task = f"{parent_query} - {question}"
    else:
        task = question

    return (
        f'Write {max_iterations} google search queries to find OFFICIAL sources online that form an objective opinion from the following task: "{task}"\n'
        f"Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.\n"
        f'You must respond with a list of strings in the following format: ["query 1", "query 2", "query 3"].\n'
        f"Focus on finding official company websites, government databases, and verified business registries.\n"
        f"The response should contain ONLY the list."
    )

def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
):
    """Generates the report prompt with emphasis on accuracy and official sources."""
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = """
You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
Every url should be hyperlinked: [url website](url)
Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report: 

eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)
ONLY use official sources such as company websites, government databases, and verified business registries.
"""
    else:
        reference_prompt = """
You MUST write all used source document names at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
Only include officially verified documents and reliable sources."
"""

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""

    structured_report_format = """
## [Company Name]: Key Points Report
#[Hashtag1] #[Hashtag2] #[Hashtag3]

### Company Overview
* Full Name: [Company's full legal name]
* Headquarters: [Street], [House Number], [City], [Country]
* Founded: [Year]
* CEO: [Name]
* Employees: [Approximate number]
* Tags of Category: [Maximum 5 Tags]
* Tech Stack [What Software are they using]
* RSS Feed: [Is an RSS Feed available if so name the link]
* Newsletter available: [yes or no if newsletter is available]
* Website: [Official URL]
* Official Social Media: [LinkedIn], [Twitter], etc.

### Business Category Segments
1. [Segment 1]
2. [Segment 2]
3. [Segment 3]
#[Hashtag6] #[Hashtag7] #[Hashtag8]

##Percent Value if they are willing to sign deals#
In Percent if you think they want to sign contracts: [0-100%]


### Recent Developments (Verified News Only)
* [Date]: [Development 1]
* [Date]: [Development 2]
#[Hashtag9] #[Hashtag10]

### Financial Metrics (From Latest Official Report)
* [Metric 1]: [Value]
* [Metric 2]: [Value]
* [Metric 3]: [Value]
#FinancialPerformance #InvestorMetrics

### Future Outlook (Based on Official Statements)
* [Point 1]
* [Point 2]
* [Point 3]
#FutureTech #MarketExpansion

### Key Business Categories
1. [Category 1]
2. [Category 2]
3. [Category 3]
#[Hashtag11] #[Hashtag12] #[Hashtag13]

Note: If any section cannot be filled with verified information from official sources, state "Information not available from official sources" rather than including unverified data.
"""

    return f"""
Information: "{context}"
---
Using the above information, answer the following query or task: "{question}" in a detailed report --
The report should follow this structure:

{structured_report_format}

Please follow all of the following guidelines in your report:
- CRUCIAL ACCURACY CHECK: You MUST perform these verification steps:
  1. Cross-reference all information with official company sources
  2. Verify company identity multiple times to avoid any mix-ups
  3. Check all numbers and dates at least 5 times
  4. Confirm all statements against official documentation
  5. Double-check all links are to official sources

- SOURCE VERIFICATION:
  * ONLY use official company websites, verified social media, official financial reports, and regulatory filings
  * Do NOT include information from unofficial sources, news aggregators, or unverified websites
  * If information cannot be verified through official sources, clearly state this fact
  * Never make assumptions or include speculative information

- CONTENT REQUIREMENTS:
  * You MUST write the report with markdown syntax and {report_format} format
  * Use in-text citation references with markdown hyperlinks: ([in-text citation](url))
  * {reference_prompt}
  * {tone_prompt}
  * The report should be comprehensive but ONLY with verified facts
  * Minimum length of {total_words} words, but accuracy takes priority over length
  * Use relevant hashtags based on verified company information

- FINAL VERIFICATION CHECKLIST:
  1. Confirm all company information matches the exact company requested
  2. Verify all financial data is from official reports
  3. Check all dates and numbers one final time
  4. Ensure all sources are official and current
  5. Remove any uncertain or unverified information

Assume that the current date is {date.today()}.
"""

def generate_resource_report_prompt(
    question, 
    context, 
    report_source: str, 
    report_format="apa", 
    tone=None, 
    total_words=1000
):
    """Generates resource report prompt focusing on official sources."""
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = """
            You MUST include all relevant source urls from official sources only.
            Every url should be hyperlinked: [url website](url)
            Only use verified, official sources such as company websites and regulatory documents.
            """
    else:
        reference_prompt = """
            You MUST write all used official source document names at the end of the report as references.
            Verify each source's authenticity before including it.
            """

    return (
        f'"""{context}"""\n\n'
        f'Based on the above information, generate a bibliography recommendation report for the following question or topic: "{question}".\n'
        f"The report should provide a detailed analysis of each recommended resource, focusing ONLY on official and verified sources.\n"
        f"Each source must be thoroughly verified for authenticity before inclusion.\n"
        f"Focus on official company documents, government filings, and verified business records.\n"
        f"The report should be well-structured, informative, and follow Markdown syntax.\n"
        f"Include verified facts and figures whenever available.\n"
        f"Minimum length: {total_words} words, but prioritize accuracy over length.\n"
        f"Cross-check all information at least 5 times before including it.\n"
        f"{reference_prompt}"
    )

def generate_outline_report_prompt(
    question, 
    context, 
    report_source: str, 
    report_format="apa", 
    tone=None, 
    total_words=1000
):
    """Generates outline report prompt with emphasis on verified information."""
    return (
        f'"""{context}""" Using the above information, generate an outline for a research report in Markdown syntax'
        f' for the following question or topic: "{question}".\n'
        f"The outline should provide a well-structured framework focusing on official and verified information only.\n"
        f"Include sections for verified company data, official financial information, and regulatory compliance.\n"
        f"Ensure each section can be supported by official documentation.\n"
        f"The research report should be detailed, informative, and a minimum of {total_words} words.\n"
        f"Mark any sections where official information might be limited or unavailable.\n"
        f"Use appropriate Markdown syntax to format the outline and ensure readability."
    )

def generate_custom_report_prompt(
    query_prompt, 
    context, 
    report_source: str, 
    report_format="apa", 
    tone=None, 
    total_words=1000
):
    """Generates custom report prompt with emphasis on verified information."""
    return (
        f'"{context}"\n\n{query_prompt}\n\n'
        f"IMPORTANT: Use only official and verified sources.\n"
        f"Cross-check all information at least 5 times.\n"
        f"If information cannot be verified through official sources, clearly state this limitation."
    )

def auto_agent_instructions():
    return """
This task involves researching a given topic using ONLY official and verified sources. Each agent must prioritize accuracy and thorough fact-checking.

Agent types and roles:

task: "should I invest in apple stocks?"
response: 
{
    "server": "💰 Finance Agent",
    "agent_role_prompt": "You are a seasoned finance analyst AI assistant focused on official financial documents and regulatory filings. Your primary goal is to compose comprehensive, accurate reports based on verified data and official company statements."
}

task: "could reselling sneakers become profitable?"
response: 
{ 
    "server": "📈 Business Analyst Agent",
    "agent_role_prompt": "You are an experienced AI business analyst expert, your job is to fill our Database with the most usefull information  about the company i ask for, please give me just the information without long sentences. First you check on the main website that the user give you, then you check on trustedshops.de, then on dnb.com, then on billiger.de, then on handelsregister.de and then on webvalid.de, then search google.de 
    Only follow this format:
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
    "server": "🌍 Travel Agent",
    "agent_role_prompt": "You are a world-travelled AI tour guide assistant focused on official tourism data and verified location information. Your main purpose is to draft engaging reports based on official tourism resources and verified cultural information."
}
"""

def generate_summary_prompt(query, data):
    """Generates summary prompt with emphasis on verified information."""
    return (
        f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n'
        f"Focus ONLY on verified and officially sourced information.\n"
        f"If the query cannot be answered using verified information, clearly state this limitation.\n"
        f"Include only verified factual information such as numbers, stats, and quotes.\n"
        f"Cross-check all information at least 5 times before including it."
    )

# Add the necessary mappings and other utility functions
report_type_mapping = {
    ReportType.ResearchReport.value: generate_report_prompt,
    ReportType.ResourceReport.value: generate_resource_report_prompt,
    ReportType.OutlineReport.value: generate_outline_report_prompt,
    ReportType.CustomReport.value: generate_custom_report_prompt,
}

def get_prompt_by_report_type(report_type):
    """Gets the appropriate prompt generator function for the given report type."""
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
