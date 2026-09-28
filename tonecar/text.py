import re
import unicodedata
import warnings
from collections import Counter

import pandas as pd
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)


def tokenize(text):
    normalized=unicodedata.normalize('NFKC',text).upper().translate(str.maketrans({'’':"'",'‘':"'",'\x91':"'",'\x92':"'"}))
    return [w for w in re.findall(r"[A-Z]+(?:'[A-Z]+)?", normalized) if len(w) >= 2]


def fiscal_year(raw, fallback):
    # Inline DEI is near the top; avoid parsing a multi-MB tree twice.
    inline = re.search(r'<[^>]+\bname\s*=\s*["\']dei:DocumentFiscalYearFocus["\'][^>]*>\s*(20\d{2})\s*</', raw, re.I)
    if inline:
        return int(inline[1]), 'dei:DocumentFiscalYearFocus'
    soup = BeautifulSoup(raw, 'lxml')
    tag = soup.find(attrs={'name': re.compile(r'^dei:DocumentFiscalYearFocus$', re.I)})
    if tag is not None:
        value = tag.get_text(strip=True)
        if re.fullmatch(r'20\d{2}', value):
            return int(value), 'dei:DocumentFiscalYearFocus'
    # Legacy filings may spell out the year label without inline XBRL.
    cover = soup.get_text(' ', strip=True)[:6000]
    label = re.search(r'(?:fiscal\s+year|year)\s+(?:ended|ending).{0,80}?(20\d{2})', cover, re.I)
    if label:
        return int(label[1]), 'cover_fiscal_year_ended'
    return int(fallback), 'report_date_year_fallback_review_required'


def extract_mda(raw, min_words=800, issuer=None):
    # Native lxml traversal preserves the same text-node/block boundaries as
    # the original BeautifulSoup implementation without a large Python DOM.
    from lxml import html as lhtml, etree
    root = lhtml.fromstring(re.sub(r'^\s*<\?xml[^>]*\?>', '', raw))
    for node in root.xpath('//script|//style|//noscript|//*[name()="ix:header"]'):
        node.drop_tree()
    blocks = {'p','div','h1','h2','h3','h4','tr','td','section'}
    pieces=[]
    for event,node in etree.iterwalk(root,events=('start','end','comment','pi')):
        if event=='start' and isinstance(node.tag,str):
            if node.tag.lower() in blocks:pieces.append('\n')
            if node.text:pieces.append(node.text)
        elif event in {'end','comment','pi'} and node.tail:
            pieces.append(node.tail)
    text = unicodedata.normalize('NFKC', ' '.join(pieces))
    text = text.replace('\ufeff',' ').replace('\u200b',' ').replace('\x92',"'").replace('\x91',"'")
    text = re.sub(r'[^\S\n]+', ' ', text)
    text = re.sub(r'\bI\s*T\s*E\s*M\b', 'ITEM', text, flags=re.I)
    starts = list(re.finditer(r'^[ \t]*ITEM\s+7\s*[.\-:–—]?\s*MANAGEMENT', text, re.I | re.M))
    # Require the section title: prose often cites "Item 8" within MD&A.
    ends = list(re.finditer(r'^[ \t]*ITEM\s+(?:7A\b\s*[.\-:–—]?\s*QUANTITATIVE|8\b\s*[.\-:–—]?\s*(?:FINANCIAL|CONSOLIDATED))', text, re.I | re.M))
    candidates = []
    for start in starts:
        end = next((e for e in ends if e.start() > start.end()), None)
        if end is None:
            continue
        section = text[start.start():end.start()]
        n = len(tokenize(section))
        candidates.append((n, start.start(), end.start(), section))
    valid = [c for c in candidates if min_words <= c[0] <= 100000]
    extraction_method = 'item7_block_heading'
    if not valid and issuer in {'HON','INTC','MCD','MS'}:
        title = r"MANAGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS"
        if issuer=='INTC':
            opening=re.compile(r'^[ \t]*'+title+r'(?:\s*\(MD&A\)(?:\s*[–—-]\s*RESULTS\s+OF\s+OPERATIONS)?)?\s+(?=Overview|Results\s+of\s+Operations|Our\s+MD&A|Our\s+Products\s+(?:We|Our)|20\d{2}\s+was|Five\s+years\s+ago|%\s+INTEL\s+REVENUE)',re.I|re.M)
            closing=re.compile(r'^[ \t]*(?:PROPERTIES|QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES|RISK\s+FACTORS)',re.I|re.M)
        else:
            opening=re.compile(r'^[ \t]*'+title+r'\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\b',re.I|re.M)
            endings={'HON':r'RISK\s+FACTORS','MCD':r'OTHER\s+KEY\s+INFORMATION','MS':r'QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES\s+ABOUT\s+(?:MARKET\s+)?RISK|FINANCIAL\s+STATEMENTS\s+AND\s+SUPPLEMENTARY\s+DATA'}
            closing=re.compile(r'^[ \t]*(?:'+endings[issuer]+r')\b',re.I|re.M)
        parts=[]
        for start in opening.finditer(text):
            end=next((e for e in closing.finditer(text) if e.start()>start.end()),None)
            if end:
                stop=end.start();section=text[start.start():stop]
                if issuer=='HON' or (issuer=='INTC' and end.group().strip().upper()=='PROPERTIES'):
                    second_title=r'LIQUIDITY\s+AND\s+CAPITAL\s+RESOURCES' if issuer=='HON' else r'CRITICAL\s+ACCOUNTING\s+ESTIMATES'
                    second_end=r'INFORMATION\s+ABOUT\s+OUR\s+EXECUTIVE\s+OFFICERS' if issuer=='HON' else r'RISK\s+FACTORS'
                    begin2=re.search(r'^[ \t]*'+second_title+r'\b',text[stop:],re.I|re.M)
                    if begin2:
                        offset=stop+begin2.start();end2=re.search(r'^[ \t]*'+second_end+r'\b',text[stop+begin2.end():],re.I|re.M)
                        if end2:
                            stop2=stop+begin2.end()+end2.start()
                            section+='\n\n'+text[offset:stop2];stop=stop2
                n=len(tokenize(section))
                if min_words<=n<=150000:parts.append((n,start.start(),stop,section))
        if parts:valid=parts;extraction_method='issuer_heading_boundaries_'+issuer
    if not valid and issuer == 'C':
        # Citi discloses Item 7 in disjoint sections. The intervening capital
        # resources/risk-factor chapters are outside its Item 7 page ranges.
        title = r"MANAGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS"
        first_open = re.search(r'^[ \t]*' + title + r'\s+(?=EXECUTIVE\s+SUMMARY)', text, re.I | re.M)
        if first_open:
            first_close = re.search(r'^[ \t]*(?:CAPITAL\s+RESOURCES|RISK\s+FACTORS)\b', text[first_open.end():], re.I | re.M)
            if first_close:
                first_stop = first_open.end() + first_close.start()
                second_parts=[]
                for opening in re.finditer(r'^[ \t]*MANAGING\s+GLOBAL\s+RISK\s+(?!\d|TABLE\s+OF\s+CONTENTS)', text[first_stop:], re.I | re.M):
                    start2=first_stop+opening.start()
                    end2=re.search(r'^[ \t]*(?:SIGNIFICANT\s+ACCOUNTING\s+POLICIES|DISCLOSURE\s+CONTROLS\s+AND\s+PROCEDURES|MANAGEMENT[’\']S\s+ANNUAL\s+REPORT\s+ON\s+INTERNAL)',text[first_stop+opening.end():],re.I|re.M)
                    if end2:
                        stop2=first_stop+opening.end()+end2.start()
                        section=text[first_open.start():first_stop]+'\n\n'+text[start2:stop2]
                        n=len(tokenize(section))
                        if min_words <= n <= 150000:second_parts.append((n,first_open.start(),stop2,section))
                if second_parts:
                    valid=second_parts;extraction_method='disjoint_Item7_C_excluding_capital_and_risk_factors'
    if not valid and issuer == 'WMT':
        # Exhibit 13 begins with Item 2 (mapped to Item 7 by the caller)
        # and ends before the audited financial statement heading.
        for start in starts:
            end = re.search(r'^[ \t]*CONSOLIDATED\s+STATEMENTS?\s+OF\s+INCOME', text[start.end():], re.I | re.M)
            if end:
                stop = start.end() + end.start()
                section = text[start.start():stop]
                n = len(tokenize(section))
                if min_words <= n <= 100000:
                    valid.append((n, start.start(), stop, section))
        extraction_method = 'incorporated_Exhibit_13_WMT'
    if not valid and issuer in {'CAH', 'CCL'}:
        # Both issuers have years in which the substantive chapter is headed
        # by its title without an "Item 7" prefix. Require the opening prose
        # to avoid selecting the table-of-contents entry.
        title = r"MANAGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS"
        if issuer == 'CAH':
            opening = re.compile(r'^[ \t]*' + title + r'(?:\s*\(MD&A\))?\s+(?=About\s+Cardinal\s+Health|Our\s+MD&A\s+within)', re.I | re.M)
            closing = re.compile(r'^[ \t]*EXPLANATION\s+AND\s+RECONCILIATION\s+OF\s+NON-GAAP\s+FINANCIAL\s+MEASURES\b', re.I | re.M)
        else:
            opening = re.compile(r'^[ \t]*' + title + r'\s+(?=Cautionary\s+Note|Overview|Results\s+of\s+Operations)', re.I | re.M)
            closing = re.compile(r'^[ \t]*(?:SELECTED\s+FINANCIAL\s+DATA|COMMON\s+STOCK\s+AND\s+ORDINARY\s+SHARES)\b', re.I | re.M)
        for start in opening.finditer(text):
            end = next((e for e in closing.finditer(text) if e.start() > start.end()), None)
            if end:
                section = text[start.start():end.start()]
                n = len(tokenize(section))
                if min_words <= n <= 150000:
                    valid.append((n, start.start(), end.start(), section))
        if valid:
            candidates += valid
            extraction_method = 'issuer_heading_boundaries_' + issuer
    if not valid and issuer in {'DE', 'FCX', 'FDX', 'LVS', 'MELI'}:
        # The title may be incorporated after the formal Item 7 cross-reference
        # or contain issuer-specific punctuation. Each rule requires substantive
        # opening prose and an explicit next-section boundary.
        title = r"MANAGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS"
        patterns = {
            'DE': (
                r'^[ \t]*' + title + r'(?:\s+RESULTS\s+OF\s+OPERATIONS\s+FOR\s+THE\s+YEARS\s+ENDED|\s+(?:The\s+following\s+)?Management[’\']s\s+Discussion\s+and\s+Analysis\s+of\s+Financial\s+Condition)',
                r'STATEMENTS?\s+OF\s+CONSOLIDATED\s+INCOME\s+For\s+the\s+Years\s+Ended\b'),
            'FCX': (
                r'^[ \t]*ITEMS?\s+7\.?\s+AND\s+7A\.?\s*' + title + r'\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+AND\s+QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES\s+ABOUT\s+MARKET\s+RISK\.?\s+(?=In\s+Management|The\s+following)',
                r'^[ \t]*ITEM\s+8\s*[.\-:–—]?\s*FINANCIAL\s+STATEMENTS\s+AND\s+SUPPLEMENTARY\s+DATA\b'),
            'FDX': (
                r'^[ \t]*OVERVIEW\s+OF\s+FINANCIAL\s+SECTION\s+(?=The\s+financial\s+section)',
                r'^[ \t]*REPORT\s+OF\s+INDEPENDENT\s+REGISTERED\s+PUBLIC\s+ACCOUNTING\s+FIRM\b'),
            'LVS': (
                r'^[ \t]*ITEM\s+7\s*(?:[.\-:–—]\s*){1,2}' + title + r'\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+(?=The\s+following\s+discussion)',
                r'^[ \t]*ITEM\s+7A\s*(?:[.\-:–—]\s*){1,2}QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES\b'),
            'MELI': (
                r"^[ \t]*ITEM\s+7\s*[.\-:–—]?\s*MAN\s*AGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+(?=You\s+should\s+read)",
                r'^[ \t]*I\s*T\s*E\s*M\s+7\s*A\s*[.\-:–—]?\s*QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES\b'),
        }
        if issuer == 'DE':
            # Some Workiva years split "INCOME" as "INCOM E" and encode the
            # possessive in MANAGEMENT'S with an invalid Windows byte.
            patterns['DE'] = (
                r'^[ \t]*MANAGEMENT\W*S\s+DISCUSSION\s+AND\s+ANALYSIS\s+(?:RESULTS\s+OF\s+OPERATIONS\s+FOR\s+THE\s+YEARS\s+ENDED|(?=(?:The\s+following\s+)?Management\W*s\s+Discussion\s+and\s+Analysis))',
                r'^[ \t]*DEERE\s*&\s*COMPANY\s+STATEMENTS?\s+OF\s+CONSOLIDATED\s+INCOM\s*E\s+For\s+the\s+Years\s+Ended\b',
            )
        opening, closing = (re.compile(p, re.I | re.M) for p in patterns[issuer])
        embedded = []
        for start in opening.finditer(text):
            end = next((e for e in closing.finditer(text) if e.start() > start.end()), None)
            if end:
                section = text[start.start():end.start()]
                n = len(tokenize(section))
                if min_words <= n <= 150000:
                    embedded.append((n, start.start(), end.start(), section))
        if embedded:
            valid = embedded
            candidates += embedded
            extraction_method = 'issuer_substantive_heading_' + issuer
    if not valid and issuer in {'MLM', 'NUE'}:
        if issuer == 'MLM':
            opening = re.search(r'^[ \t]*MANAGEMENT\W*S\s+DISCUSSION\s*&\s*ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s*&\s*RESULTS\s+OF\s+OPERATIONS\s+INTRODUCTORY\s+OVERVIEW\b', text, re.I | re.M)
            # This incorporated annual report repeats the MD&A title on
            # every page. The first following page without that running
            # heading starts quarterly/selected financial data, not MD&A.
            pages = list(re.finditer(r'Martin\s+Marietta\s*\|\s*Page\s+\d+\s+', text, re.I))
            close = next((page for page in pages if opening and page.start() > opening.end()
                          and not re.match(r'MANAGEMENT\W*S\s+DISCUSSION\s*&\s*ANALYSIS', text[page.end():], re.I)), None)
        else:
            opening = re.search(r'^[ \t]*MANAGEMENT\W*S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+OVERVIEW\b', text, re.I | re.M)
            close = re.search(r'^[ \t]*REPORT\s+OF\s+INDEPENDENT\s+REGISTERED\s+PUBLIC\s+ACCOUNTING\s+FIRM\b', text[opening.end():] if opening else '', re.I | re.M)
            if close:
                close = (opening.end() + close.start(),)
        if opening and close:
            stop = close.start() if issuer == 'MLM' else close[0]
            section = text[opening.start():stop]
            n = len(tokenize(section))
            if min_words <= n <= 150000:
                valid = [(n, opening.start(), stop, section)]
                extraction_method = 'incorporated_Exhibit_13_page_boundary_' + issuer
    if not valid and issuer in {'JPM', 'XOM', 'BAC', 'CVX', 'IBM', 'PFE', 'UNP', 'WFC'}:
        # These issuers incorporate annual-report MD&A into the same primary document.
        # Distinguish its substantive opening from the annual-report TOC and page headers.
        title = r"MANAGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS"
        if issuer in {'IBM','PFE','UNP','WFC'}:
            opening = re.compile(r"^[ \t]*(?:MANAGEMENT[’']?S?\s+DISCUSSION(?:\s+AND\s+ANALYSIS)?|FINANCIAL\s+REVIEW)\b",re.I|re.M)
            closing = re.compile(r"^[ \t]*(?:REPORT\s+OF\s+(?:INDEPENDENT|MANAGEMENT)|MANAGEMENT[’']S\s+(?:RESPONSIBILITY|REPORT)|CONSOLIDATED\s+(?:STATEMENTS?|FINANCIAL\s+STATEMENTS))",re.I|re.M)
        elif issuer == 'CVX':
            opening = re.compile(r'^[ \t]*' + title + r'\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+(?:FINANCIAL\s+TABLE\s+OF\s+CONTENTS\s+)?(?=KEY\s+FINANCIAL\s+RESULTS|BUSINESS\s+ENVIRONMENT)',re.I|re.M)
            # The income statement is an MD&A discussion subheading here.
            closing = re.compile(r"^[ \t]*(?:REPORT\s+OF\s+INDEPENDENT|MANAGEMENT[’']S\s+(?:RESPONSIBILITY|REPORT))",re.I|re.M)
        elif issuer == 'BAC':
            opening = re.compile(r'^[ \t]*' + title + r'\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+(?=Bank\s+of\s+America\s+Corporation)', re.I | re.M)
            closing = re.compile(r'^[ \t]*ITEM\s+(?:7A\b\s*[.\-:–—]?\s*QUANTITATIVE|8\b\s*[.\-:–—]?\s*(?:FINANCIAL|CONSOLIDATED))', re.I | re.M)
        elif issuer == 'JPM':
            opening = re.compile(r'^[ \t]*' + title + r'\s+(?=(?:The\s+following\s+is\s+Management|This\s+section\s+of\s+JPMorgan))', re.I | re.M)
            closing = re.compile(r"^[ \t]*(?:FIVE[\-– ]YEAR\s+STOCK\s+PERFORMANCE|MANAGEMENT[’']S\s+REPORT\s+ON\s+INTERNAL\s+CONTROL|REPORT\s+OF\s+INDEPENDENT\s+REGISTERED)", re.I | re.M)
        else:
            opening = re.compile(r'^[ \t]*' + title + r'\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s+(?=FUNCTIONAL\s+EARNINGS|FORWARD[\-– ]LOOKING\s+STATEMENTS\s+(?:Statements|The|This|Certain|Outlooks))', re.I | re.M)
            closing = re.compile(r"^[ \t]*(?:MANAGEMENT[’']S\s+REPORT|REPORT\s+OF\s+INDEPENDENT\s+REGISTERED|CONSOLIDATED\s+STATEMENT\s+OF\s+INCOME)", re.I | re.M)
        embedded = []
        for start in opening.finditer(text):
            end = next((e for e in closing.finditer(text) if e.start() > start.end()), None)
            if end is None:
                continue
            section = text[start.start():end.start()]
            n = len(tokenize(section))
            if min_words <= n <= 150000:
                embedded.append((n, start.start(), end.start(), section))
        if embedded:
            valid = embedded
            candidates += embedded
            extraction_method = 'embedded_annual_report_' + issuer
    if not valid:
        raise ValueError(f'MD&A requires manual review: {len(starts)} starts; word counts {[c[0] for c in candidates]}')
    chosen = max(valid)
    # A cross-reference or TOC can exceed the word threshold when a broad
    # fallback runs into later 10-K chapters. Never score it as actual MD&A.
    opening = re.sub(r'\s+', ' ', chosen[3][:1200])
    if issuer in {'CVX','IBM','PFE','UNP','WFC'} and (
        re.search(r'information required by this ITEM is incorporated by reference', opening, re.I)
        or re.search(r'^\s*management discussion overview.{0,40}pages', opening, re.I)
        or (issuer=='CVX' and re.search(r'7A\.\s*Quantitative.{0,120}8\.\s*Financial', opening, re.I))
    ):
        raise ValueError('Cross-reference/TOC selected instead of substantive MD&A; use Exhibit 13')
    return chosen[3], {'candidate_count': len(candidates), 'valid_candidates': len(valid),
                       'word_count': chosen[0], 'start': chosen[1], 'end': chosen[2],
                       'first_300': chosen[3][:300], 'last_300': chosen[3][-300:],
                       'extraction_method': extraction_method,
                       'manual_review_required': True}


def load_lm(path):
    df = pd.read_csv(path)
    required = {'Word', 'Positive', 'Negative', 'Uncertainty'}
    if not required.issubset(df.columns):
        raise ValueError('Not an LM Master Dictionary CSV')
    return {c.lower(): set(df.loc[pd.to_numeric(df[c], errors='raise') > 0, 'Word'].str.upper())
            for c in ['Positive', 'Negative', 'Uncertainty']}


def score(text, lexicon):
    tokens = tokenize(text)
    if not tokens:
        raise ValueError('Empty text')
    counts = Counter(tokens)
    result = {'word_count': len(tokens)}
    for category, words in lexicon.items():
        count = sum(counts[w] for w in words)
        result[category + '_count'] = count
        result[category + '_rate'] = count / len(tokens)
    result['tone'] = result['positive_rate'] - result['negative_rate']
    return result
