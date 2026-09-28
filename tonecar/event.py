import numpy as np
import pandas as pd
import statsmodels.api as sm


def event_position(sessions, filing_date, acceptance=None, rule='same'):
    date = pd.Timestamp(filing_date).normalize()
    if rule == 'next':
        return int(sessions.searchsorted(date, side='right'))
    if rule == 'acceptance' and acceptance:
        stamp = pd.Timestamp(acceptance)
        stamp = stamp.tz_localize('America/New_York') if stamp.tzinfo is None else stamp.tz_convert('America/New_York')
        date = stamp.tz_localize(None).normalize()
        # At/after regular close belongs to the next session (early closes supplied by caller).
        if stamp.hour >= 16:
            return int(sessions.searchsorted(date, side='right'))
    return int(sessions.searchsorted(date, side='left'))


def study(stock, market, sessions, position, estimation=(-120, -20), minimum=80, windows=((-1, 1), (-3, 3), (-5, 5))):
    if position + estimation[0] < 0 or position + max(w[1] for w in windows) >= len(sessions):
        raise ValueError('Insufficient calendar coverage')
    # Reindex BEFORE slicing; missing prices must never compress the event clock.
    returns = pd.DataFrame({'stock': stock, 'market': market}).reindex(sessions)
    train = returns.iloc[position + estimation[0]:position + estimation[1] + 1].dropna()
    if len(train) < minimum or train.market.std() < 1e-12:
        raise ValueError('Insufficient/nonvarying estimation data')
    fit = sm.OLS(train.stock, sm.add_constant(train.market)).fit()
    lo, hi = min(w[0] for w in windows), max(w[1] for w in windows)
    event = returns.iloc[position + lo:position + hi + 1].copy()
    if event.isna().any().any():
        raise ValueError('Missing event return; event excluded')
    event['relative_day'] = np.arange(lo, hi + 1)
    event['expected_return'] = fit.params['const'] + fit.params['market'] * event.market
    event['abnormal_return'] = event.stock - event.expected_return
    result = {'alpha': fit.params['const'], 'beta': fit.params['market'],
              'estimation_n': len(train), 'estimation_r2': fit.rsquared,
              'event_session': str(sessions[position].date())}
    for a, b in windows:
        result[f'car_{a}_{b}'] = event.loc[event.relative_day.between(a, b), 'abnormal_return'].sum()
        result[f'mar_{a}_{b}'] = (event.loc[event.relative_day.between(a, b), 'stock'] - event.loc[event.relative_day.between(a, b), 'market']).sum()
    return result, event
