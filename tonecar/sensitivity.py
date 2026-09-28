"""Conservative numeric-table classifier for a separate sensitivity measure."""
import re
import numpy as np
from .text import tokenize

def numeric_table(node):
    if node.xpath('.//table'):
        return False
    rows=node.xpath('.//tr')
    texts=[' '.join(c.itertext()).strip() for c in node.xpath('.//td|.//th')]
    cells=[s for s in texts if s]
    numeric=sum(bool(re.search(r'\d',s)) and not re.search(r'[A-Za-z]{3}',s) for s in cells)
    if re.search(r'ITEM\s+(?:7|8)|MANAGEMENT.{0,15}DISCUSSION|CONSOLIDATED\s+STATEMENTS',' '.join(texts),re.I):
        return False
    if any(len(tokenize(s))>60 for s in cells):
        return False
    return len(rows)>=2 and len(cells)>=6 and numeric>=4 and numeric/len(cells)>=.35

def excess_buy_hold(stock,market):
    """Difference of compounded simple returns, not a sum of daily AR."""
    return np.prod(1+np.asarray(stock))-np.prod(1+np.asarray(market))
